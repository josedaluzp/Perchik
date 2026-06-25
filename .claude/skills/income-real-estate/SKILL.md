---
name: income-real-estate
description: Use to enter real-estate rental income for a 1065 in CCH Axcess — Rent & Royalty worksheet plus depreciation. An income module dispatched by income-router. AUTO + REGLA.
---

# income-real-estate — Rent & Royalty + depreciación

## Qué hace
Carga el income de real estate (alquileres) y la depreciación.

## Depende de
- **source-resolver** → `income.qb_profit_and_loss`.
- **qb-report-reader** → líneas del P&L.
- **cch-axcess-client** → escribe en Rent & Royalty.

## Mapeo / reglas
- Ingresos de alquiler → Rent & Royalty.
- Gastos operativos → líneas correspondientes.
- **Depreciación:** activos buildings/land + amortización acumulada.
- **Fair Rental Days** por propiedad.

## Verificaciones
- Net rental cuadra con el P&L de QB.
