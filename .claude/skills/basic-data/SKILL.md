---
name: basic-data
description: Use to populate the partnership's identity in CCH Axcess for a 1065 — legal name, EIN, address, entity type (Domestic LLC), and accounting method (cash/accrual). Stage 1 of the return. AUTO + CHECK.
---

# basic-data — identidad de la sociedad (etapa 1)

## Qué hace
Llena los datos maestros de la sociedad en CCH (Basic Data – General).

## Depende de
- **source-resolver** → `entity.ss4`, `entity.operating_agreement`, `entity.record`.
- **dropbox-connector / airtable-connector (MCP)**, **qb-report-reader** (método contable).
- **cch-axcess-client** → escribe.

## Mapeo (fuente → campo CCH)
| Dato | Fuente | Campo CCH |
|------|--------|-----------|
| Nombre legal | SS-4 / Airtable | Basic Data – General |
| EIN | SS-4 | Basic Data – General |
| Dirección | SS-4 / OA | Basic Data – General |
| **Type of entity filing** (Domestic LLC) | OA / Airtable | Other Info → **fila nueva** (BRECHA v2.3) |
| **Método contable** (Cash/Accrual) | pie del P&L (qb-report-reader) | Basic Data – General → **fila nueva** (BRECHA v2.3) |

## Verificaciones (CHECK)
- EIN con formato válido.
- Nombre legal == el del SS-4 (no el comercial).

## Brechas (de pendientes v2.4)
- "Type of entity filing this return" no era fila en v2.3 → agregada aquí.
- Método contable no era fila de mapping en v2.3 → agregado aquí.
