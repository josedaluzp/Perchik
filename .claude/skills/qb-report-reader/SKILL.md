---
name: qb-report-reader
description: Use when a 1065→CCH Axcess skill needs numbers out of a QuickBooks report PDF (Profit & Loss, Balance Sheet) stored in Dropbox. Parses the PDF into structured line items. Does NOT decide where the file lives (ask source-resolver) nor where the numbers go in CCH (that's the consuming skill).
---

# qb-report-reader — parser de reportes QuickBooks

## Qué hace

Convierte un PDF de reporte de QuickBooks (P&L, Balance Sheet) en **líneas
estructuradas** `{ account, amount }`. Es un normalizador: entra un PDF, sale data limpia.

## Depende de
- **source-resolver** → para saber qué archivo pedir (`income.qb_profit_and_loss`,
  `income.qb_balance_sheet`).
- **dropbox-connector (MCP)** → para traer el PDF.

No conoce el 1065. No sabe a qué campo de CCH va cada cuenta.

## Entrada
- `pdf` — el PDF de QB ya descargado (la skill consumidora lo trajo vía resolver+Dropbox).
- `report_type` — `profit_and_loss` | `balance_sheet`.

## Salida
```yaml
report_type: profit_and_loss
period: "2024-01-01..2024-12-31"
accounting_method: cash        # cash | accrual (del pie del reporte)
lines:
  - account: "Rental Income"
    amount: 120000.00
  - account: "Depreciation Expense"
    amount: -18000.00
totals:
  net_income: 84000.00
```

## Procedimiento
1. Detectar el tipo de reporte por encabezado.
2. Extraer método contable (cash/accrual) del pie — lo necesita basic-data.
3. Parsear cada fila a `{ account, amount }`, signo según ingreso/gasto.
4. Devolver totales para que cross-check-engine pueda cuadrar después.

## Reglas
- **Redondeo del balance:** ≥ 0.50 hacia arriba (regla de SALVIN7 PII).
- No interpretar cuentas: devolver el nombre tal cual aparece. El mapeo cuenta→campo CCH
  es responsabilidad de la skill de income/balance.

## Brechas / a verificar
- Robustez del parseo cuando QB exporta en layout multi-columna. Validar con un PDF real.
