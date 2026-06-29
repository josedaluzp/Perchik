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

## Procedimiento

1. **Resolver** vía source-resolver el campo del trigger (`primary_form_status`) y su valor de
   disparo (`CCH To do`).
2. **Buscar** entidades con `Primary Form Status = "CCH To do"` (Entity Tracker).
3. **Por cada entidad, en serie (una a la vez):** invocar `return-orchestrator` con
   `client = <entidad>` → extrae las fuentes (Airtable + Dropbox) y arma el borrador/mockup.
4. **Devolver** el resumen de lo procesado (ver Salida).

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
- **Solo lectura en Airtable.** No escribe `Primary Form Status` ni ningún otro campo. Tampoco
  escribe en CCH (eso es de `cch-axcess-client`, que aún no existe).
- En serie, no en paralelo: una entidad a la vez para no pisar conexiones MCP ni dejar varios
  borradores a medio armar.
- No clasifica ni mapea — eso es de `scenario-classifier` / orquestador.

## Idempotencia (limitación actual)

Como NO hay writeback de estado, cada corrida vuelve a procesar **todas** las entidades que
sigan en `CCH To do`. Es inofensivo (solo lectura) pero genera borradores repetidos y consumo.
Mitigación por ahora — elegir una:
- **Manual:** el equipo mueve la entidad fuera de `CCH To do` en Airtable cuando el borrador ya
  fue revisado (su flujo normal de tablero).
- **Disparo puntual:** correr el trigger a demanda en vez de en cron, hasta activar el writeback.

Cuando se decida automatizar el ciclo, se reactiva el bloque de estados (abajo).

## Estados — diferido (NO activo todavía)

El campo `Primary Form Status` tiene el state-machine completo y sus choice IDs ya están
documentados en `source-resolver` → `connectors.airtable.status_states`
(`cch_in_progress`, `cch_ready_check`, `cch_corregir`). El diseño previsto, **para cuando se
active**, es: al tomar la entidad escribir `CCH In progress` (idempotencia), y al terminar
`CCH Ready to Check` (éxito) o `CCH Corregir` (fallo). Requiere que el conector Airtable tenga
permiso de **escritura**. **Por ahora esto no se ejecuta.**

## Cómo se ejecuta (Tareas Programadas de Cowork)

Corre en una **PC dedicada con Cowork abierto** y *"Mantener activo"* encendido (las tareas
programadas sólo corren con el equipo activo). El prompt de cada tarea programada es:

> **Ejecutá la skill `intake-trigger`.** Revisá Airtable por las entidades en
> `Primary Form Status = "CCH To do"`, y por cada una armá su borrador 1065 con
> `return-orchestrator` (extracción de datos + mockup). NO cambies ningún estado en Airtable.
> Devolveme el resumen de lo procesado.

> **Por qué Cowork y no routines/API:** las tareas programadas de Cowork corren en la misma
> sesión local autenticada → los conectores MCP (Airtable, Dropbox) están vivos. Una routine
> cloud headless podría despertar sin esos conectores autenticados.
