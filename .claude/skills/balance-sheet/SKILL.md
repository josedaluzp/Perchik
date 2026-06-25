---
name: balance-sheet
description: Use to populate Schedule L / M-1 / M-2 for a 1065 in CCH Axcess from the QuickBooks balance sheet. Stage 7. AUTO + REGLA. Handles the suppressed-balance diagnostic case.
---

# balance-sheet — Schedule L / M-1 / M-2 (etapa 7)

## Qué hace
Llena el balance (Sch L) y las conciliaciones M-1 / M-2.

## Depende de
- **source-resolver** → `income.qb_balance_sheet`.
- **qb-report-reader** → parsea el PDF.
- **cch-axcess-client** → escribe.

## Mapeo / reglas
- **Umbral de balance 1M / 250k:** si está por debajo, se puede suprimir Sch L.
- **Balance suprimido PERO** el diagnostic igual exige **buildings/land activos +
  amortización acumulada** (sin las propiedades vendidas). Completar esa parte.
- **Schedule M-2 (Increases/Decreases):** va también en el escenario **estándar**
  (SALVIN7 lo carga: FOREIGN SERVICE INCOME / expenses para que impacte el balance),
  no solo en cambio accionario.
- **Redondeo:** ≥ 0.50 hacia arriba.

## Verificaciones
- M-1 cuadra net income contable vs fiscal.
- M-2 cuadra cuentas de capital con partners-k1.

## Brechas (de pendientes v2.4)
- M-2 en Escenario A (v2.3 solo lo tenía en Escenario C).
- Nota del balance suprimido que igual exige buildings/land + amortización.
