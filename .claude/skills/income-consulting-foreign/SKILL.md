---
name: income-consulting-foreign
description: Use to enter foreign-source consulting income for a 1065 in CCH Axcess — with the FOREIGN-prefixed M-1 / M-2 entries so it impacts the balance correctly. An income module dispatched by income-router. REGLA.
---

# income-consulting-foreign — consulting foreign (M-1 + M-2 FOREIGN)

## Qué hace
Carga income de consulting de fuente **foreign**, con el tratamiento M-1/M-2 que lo hace
impactar el balance.

## Depende de
- **source-resolver** → `income.qb_profit_and_loss`.
- **qb-report-reader**, **cch-axcess-client**.

## Mapeo / reglas
- Ingreso foreign service → con prefijo **FOREIGN SERVICE INCOME** en M-2.
- Expenses foreign → en M-2 (decreases).
- Coordinar con **balance-sheet** (M-2 estándar) y **foreign-forms** (K-2/K-3 columna Foreign).

## Notas
- Caso C1 (SALVIN7). Va junto con income-passthrough-k1 cuando además recibe K-1.
