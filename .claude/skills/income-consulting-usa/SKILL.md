---
name: income-consulting-usa
description: Use to enter US-source consulting/service income for a 1065 in CCH Axcess — page 1 (line 1a / line 7). An income module dispatched by income-router. AUTO + REGLA.
---

# income-consulting-usa — consulting USA (página 1)

## Qué hace
Carga income de servicios/consulting de fuente US en página 1 del 1065.

## Depende de
- **source-resolver** → `income.qb_profit_and_loss`.
- **qb-report-reader**, **cch-axcess-client**.

## Mapeo / reglas
- Ingreso bruto de servicios → **línea 1a**.
- Otros ingresos → **línea 7** según corresponda.
- Gastos → líneas de deducciones de página 1.

## A verificar (de pendientes v2.4)
- **Business code de consulting:** video SALVIN7 muestra ~`541600`; doc v2.3 dice `541990`.
  Confirmar el correcto.
