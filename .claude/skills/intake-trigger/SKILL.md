---
name: intake-trigger
description: Use to detect that a 1065 return is ready to process — watches Airtable for an entity whose "Primary Form Status" = "CCH To do" and kicks off the return-orchestrator for that client. The entry point of the whole pipeline. Lo invocan las Tareas Programadas de Cowork a varios horarios.
---

# intake-trigger — el disparo

## Qué hace

Es el **punto de entrada** del pipeline. Lo invocan las **Tareas Programadas de Cowork**
(Claude Desktop) a varios horarios del día. En cada corrida busca en Airtable las entidades
listas y dispara la **extracción de datos + armado del borrador** (`return-orchestrator`) para
cada una.

**Condición de disparo (lo único que mira por ahora):**
`entities."Primary Form Status" == "CCH To do"`. Ese estado significa *"extraer los datos y armar
el borrador"*.

> **Alcance actual:** el trigger es **solo lectura sobre Airtable**. NO escribe estados de
> vuelta. El manejo del ciclo de estados (`In progress` / `Ready to Check` / `Corregir`) está
> diseñado pero **desactivado por ahora** (ver "Estados — diferido"). Hoy: detectar `CCH To do`
> → extraer → entregar borrador.

No clasifica ni mapea nada — solo detecta y delega.

## Depende de
- **source-resolver** → header `connectors.airtable` (base/tabla y campo del trigger).
- **airtable-connector (MCP)** → leer el estado (solo lectura).
- **return-orchestrator** → la extracción + armado real, uno por entidad.
- **completion-report** → tras cada entidad, manda el mail de cierre (éxito o fallo). Es el
  único punto que notifica; el orquestador (doble uso: también corre a mano) NO manda mail.

## Procedimiento

1. **Resolver** vía source-resolver el campo del trigger (`primary_form_status`) y su valor de
   disparo (`CCH To do`).
2. **Buscar** entidades con `Primary Form Status = "CCH To do"` (Entity Tracker).
   - **Si no hay ninguna:** NO correr el orquestador. Invocar `completion-report` en modo
     `empty` → manda un mail corto avisando que no había formularios para enviar a CCH. Terminar.
3. **Tomar como máximo `batch_limit` (= 5) entidades** de la lista (las primeras). El resto queda
   para la próxima corrida horaria.
4. **Por cada una de esas ≤5, en serie (una a la vez):**
   a. invocar `return-orchestrator` con `client = <entidad>` → extrae las fuentes
      (Airtable + Dropbox), arma el borrador/mockup y devuelve el resultado estructurado
      (`result`, `mockup`, `fields_by_status`, `qa`, `cch_upload`).
   b. invocar `completion-report` con ese resultado → manda el mail de cierre (éxito o fallo).
5. **Devolver** el resumen de lo procesado (ver Salida), incluyendo cuántas quedaron pendientes.

## Salida
```yaml
run_at: 2026-06-29T14:00         # informativo (lo estampa el entorno)
triggered:
  - client: SALVIN7
    result: success
    mockup: docs/mockup-1065-salvin7.html
  - client: AGGUILU
    result: failure
    reason: "No se encontró el P&L del año en Dropbox"
```

## Reglas
- **Límite de lote: `batch_limit = 5` por corrida.** Nunca procesar más de 5 entidades en una
  corrida horaria (evita runs eternos y avalancha de borradores). El resto espera a la próxima hora.
- **Corrida vacía:** si no hay ninguna en `CCH To do`, no correr el orquestador; solo notificar
  vía `completion-report` (modo `empty`).
- **Solo lectura en Airtable.** No escribe `Primary Form Status` ni ningún otro campo. Tampoco
  escribe en CCH (eso es de `cch-axcess-client`, que aún no existe).
- En serie, no en paralelo: una entidad a la vez para no pisar conexiones MCP ni dejar varios
  borradores a medio armar.
- No clasifica ni mapea — eso es de `scenario-classifier` / orquestador.

## Idempotencia (limitación actual)

Como NO hay writeback de estado, cada corrida vuelve a tomar las mismas entidades que sigan en
`CCH To do` (acotadas a `batch_limit = 5`). Es inofensivo (solo lectura) pero genera borradores
repetidos. Mitigación por ahora:
- **Manual:** el equipo mueve la entidad fuera de `CCH To do` cuando el borrador ya fue revisado.
  Con el límite de 5, cada hora se toman las 5 de arriba; al sacarlas, la próxima hora suben las
  siguientes 5 (funciona como una cola natural).
- Cuando se decida automatizar el ciclo, se reactiva el writeback de estados (bloque abajo).

## Estados — diferido (NO activo todavía)

El campo `Primary Form Status` tiene el state-machine completo y sus choice IDs ya están
documentados en `source-resolver` → `connectors.airtable.status_states`
(`cch_in_progress`, `cch_ready_check`, `cch_corregir`). El diseño previsto, **para cuando se
active**, es: al tomar la entidad escribir `CCH In progress` (idempotencia), y al terminar
`CCH Ready to Check` (éxito) o `CCH Corregir` (fallo). Requiere que el conector Airtable tenga
permiso de **escritura**. **Por ahora esto no se ejecuta.**

## Cómo se ejecuta (Tareas Programadas de Cowork)

Corre en una **PC dedicada con Cowork abierto** y *"Mantener activo"* encendido (las tareas
programadas sólo corren con el equipo activo). Tarea `intake-1065-cch`, **frecuencia: cada 1 hora**.
El prompt (ver también `docs/tarea-programada-intake-1065-cch.md`):

> Revisá en Airtable las entidades en `Primary Form Status = "CCH To do"`. Por cada una, en serie:
> 1) armá su borrador 1065 con `return-orchestrator` (extracción + mockup); 2) ejecutá
> `completion-report` para notificar por mail (Gmail) que el 1065 se completó, con los puntos a
> verificar y la referencia al mockup. NO cambies ningún estado en Airtable. Devolveme el resumen.

> **Por qué Cowork y no routines/API:** las tareas programadas de Cowork corren en la misma
> sesión local autenticada → los conectores MCP (Airtable, Dropbox, Gmail) están vivos. Una routine
> cloud headless podría despertar sin esos conectores autenticados.
