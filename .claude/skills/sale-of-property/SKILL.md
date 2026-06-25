---
name: sale-of-property
description: Use to enter a sale of real property for a 1065 in CCH Axcess — Schedule D / Form 4797, the unrecaptured §1250 (9c) amount, and the 8804 corp-vs-individual Section 1446 distinction. An income module dispatched by income-router. REGLA + CHECK.
---

# sale-of-property — venta de propiedades (Sch D / 4797 / 9c / 8804)

## Qué hace
Carga la venta de propiedad y su cadena completa hasta el 8804/8805.

## Depende de
- **source-resolver** → `sale.real_estate_hud`, `sale.depreciation_schedule`,
  `income.qb_profit_and_loss`, y (si existe) `reference.finished_1065`.
- **qb-report-reader**, **cch-axcess-client**.

## Cálculo de la venta (por propiedad)
Para cada propiedad 100% dispuesta (building + land por separado):
- **Sales price**: del HUD (`sale.real_estate_hud`). Total → Form 4797 línea 1A.
- **Sales price Building** = sale price total − Land.
- **Adjusted basis** = costo − depreciación acumulada.
- **Gain** = sales price − adjusted basis − expense of disposition.
- **Net §1231 gain** = Σ gains de todas las propiedades → **Schedule K línea 10**.

## ⚠️ Unrecaptured §1250 gain (9c) — REGLA EXACTA (no estimar)
El 9c es el error más común. La regla:

> **9c = el MENOR de (a) la depreciación ACUMULADA de toda la vida de los edificios
> vendidos, y (b) la ganancia reconocida.** NO es la depreciación del año.

- La depreciación acumulada sale de `sale.depreciation_schedule` (Property List / Form 4562 /
  detalle de activos), **no** de la línea "Depreciation Expense" del P&L (esa es solo el año).
- **Si existe el 1065 ya armado** (`reference.finished_1065`): leer el **valor exacto del
  Form 4797 / Statement "unrecaptured §1250"** en vez de calcular. Ese es la verdad.
- Va a **Schedule K línea 9c**.

**Ejemplo real (AGGUILU 2025):** vendió 16596 Whitcomb (deprec. acum. building **17,115**)
y 13955 Prevost (**17,117**). 9c = 17,115 + 17,117 = **34,232**. (Estimar con la depreciación
del año daba ~20,066 → MAL.)

## Cadena completa
**9c (34,232) + resto del 1231 gain → línea 10 (35,769) → 4m / 4q del 8804 → K-2 / K-3.**

## Distinción CORP vs INDIVIDUAL (la pasa a foreign-forms)
- El gain se asigna a cada socio por su %.
- **Socios NO corporativos (individuos):** su parte de 9c va a **8804 línea 4m** (×25%);
  su parte de adjusted net capital gain va a **4q** (×20%).
- **Socios corporativos:** su parte va a la ECTI corporativa **línea 4a** (×21%), que se
  compensa con la pérdida de actividad — suele dar 0.
- partners-k1 provee el tipo de entidad y el % de cada socio.

## Verificaciones (CHECK)
- 9c = Σ depreciación acumulada de los edificios vendidos (capada al gain).
- Form 4797 == 1065 página 5.
- Σ gains por socio = línea 10; cadena 9c → 10 → 4m/4q consistente.
