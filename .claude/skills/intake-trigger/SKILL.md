---
name: intake-trigger
description: Use to detect that a 1065 return is ready to process — watches Airtable for an entity whose "Primary Form Status" = "CCH To do" and kicks off the return-orchestrator for that client. The entry point of the whole pipeline. Lo invocan las Tareas Programadas de Cowork a varios horarios.
---

# intake-trigger — el disparo

## Qué hace

Es el **punto de entrada** del pipeline. Lo invocan las **Tareas Programadas de Cowork**
(Claude Desktop) a varios horarios del día. En cada corrida: busca en Airtable las entidades
listas para procesar, las **marca como "en proceso"** (para que la próxima corrida no las
vuelva a agarrar), y dispara `return-orchestrator` para cada una.

**Condición de disparo:** `entities."Primary Form Status" == "CCH To do"`.

No clasifica ni mapea nada — solo detecta, reserva (writeback de estado) y delega.

## Depende de
- **source-resolver** → header `connectors.airtable` (base/tabla del trigger + `status_states`).
- **airtable-connector (MCP)** → leer estados y **escribir** el cambio de estado (writeback).
- **return-orchestrator** → el pipeline real, uno por entidad.

## State machine del estado (Primary Form Status)

Usa los IDs definidos en `source-resolver` → `connectors.airtable.status_states`
(escribir por choice id, nunca por nombre):

```
CCH To do ──(la tarea lo agarra)──▶ CCH In progress
                                          │
                  ┌───────────────────────┴───────────────┐
             borrador OK                                 falló algo
                  │                                          │
                  ▼                                          ▼
          CCH Ready to Check                           CCH Corregir
          (revisión humana)                       (intervención manual)
```

## Procedimiento

1. **Resolver** vía source-resolver: el campo del trigger (`primary_form_status`) y el bloque
   `status_states` con los 4 choice ids (`cch_todo`, `cch_in_progress`, `cch_ready_check`,
   `cch_corregir`).
2. **Buscar** entidades con `Primary Form Status = "CCH To do"` (Entity Tracker).
3. **Por cada entidad, en serie (una a la vez):**
   a. **Reservar:** escribir `Primary Form Status = "CCH In progress"` (writeback Airtable por
      MCP, usando el choice id `cch_in_progress`). Esto se hace **ANTES** de procesar → así si la
      tarea tarda o se solapa con otra corrida, la entidad ya no aparece en el filtro `CCH To do`.
   b. **Procesar:** invocar `return-orchestrator` con `client = <entidad>`.
   c. **Cerrar según resultado:**
      - Éxito (borrador + mockup generados) → escribir `CCH Ready to Check` (`cch_ready_check`).
      - Fallo (falta P&L / dato crítico / excepción) → escribir `CCH Corregir` (`cch_corregir`)
        y registrar el motivo en la salida. **Nunca** dejar la entidad colgada en `In progress`.
4. **Devolver** el resumen de lo disparado (ver Salida).

## Salida
```yaml
run_at: 2026-06-29T14:00         # informativo (lo estampa el entorno)
triggered:
  - client: SALVIN7
    result: ready_to_check
    mockup: docs/mockup-1065-salvin7.html
  - client: AGGUILU
    result: corregir
    reason: "No se encontró el P&L del año en Dropbox"
skipped: 0                        # ya estaban fuera de 'CCH To do'
```

## Reglas
- **Idempotente:** el writeback a `CCH In progress` ocurre ANTES de procesar; es la garantía de
  no disparar dos veces la misma entidad. Si una entidad ya no está en `CCH To do` al momento de
  reservarla (otra corrida la tomó), saltarla.
- **El trigger es el ÚNICO dueño del ciclo de estado** de `Primary Form Status` mientras corre el
  pipeline (`To do → In progress → Ready to Check | Corregir`). Las skills del pipeline no tocan
  ese campo. Los estados posteriores (`to Approve`, `Out for Signature`, etc.) son del flujo
  manual del equipo.
- **Sólo escribe en Airtable** (el campo de estado). **Nunca escribe en CCH** — eso es de
  `cch-axcess-client`, que aún no existe.
- En serie, no en paralelo: procesar una entidad a la vez para no pisar conexiones MCP ni dejar
  varios borradores a medio armar.
- No clasifica ni mapea — eso es de `scenario-classifier` / orquestador.

## Cómo se ejecuta (Tareas Programadas de Cowork)

Corre en una **PC dedicada con Cowork abierto** y *"Mantener activo"* encendido (las tareas
programadas sólo corren con el equipo activo). Se crean varias tareas a distintos horarios.
El prompt de cada tarea programada es simplemente:

> **Ejecutá la skill `intake-trigger`.** Revisá Airtable por las entidades en
> `Primary Form Status = "CCH To do"`, marcá cada una como `CCH In progress`, armá su borrador
> 1065 con `return-orchestrator`, y dejá el estado final en `CCH Ready to Check` (o
> `CCH Corregir` si algo falló). Devolveme el resumen de lo procesado.

> **Por qué Cowork y no routines/API:** las tareas programadas de Cowork corren en la misma
> sesión local autenticada → los conectores MCP (Airtable, Dropbox) están vivos. Una routine
> cloud headless podría despertar sin esos conectores autenticados.
