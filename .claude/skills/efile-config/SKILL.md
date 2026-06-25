---
name: efile-config
description: Use to configure Electronic Filing for a 1065 in CCH Axcess — e-file options, Form 8879-PE, Preparer info, and the ERO override. Stage 4. AUTO + REGLA.
---

# efile-config — Electronic Filing + 8879 + Preparer (etapa 4)

## Qué hace
Configura el e-file del return.

## Depende de
- **source-resolver** → `entity.record` (datos del preparador, si están en Airtable).
- **cch-axcess-client** → escribe.

## Mapeo / reglas
- **Electronic Filing:** activar.
- **Form 8879-PE:** firma autorizada.
- **Preparer:** datos del preparador.
- **ERO – Electronic Return Originator (overrides):** marcar el primer punto.

## Brechas (de pendientes v2.4)
- ERO overrides (marcar primer punto) no figuraba en v2.3 → agregado.
