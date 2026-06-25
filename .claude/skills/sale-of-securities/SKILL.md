---
name: sale-of-securities
description: Use to enter a sale of securities (stocks) for a 1065 in CCH Axcess via Form 8949 — with the rule that short/long-term gains are EXCLUDED from Section 1446 withholding. An insertable income module (Case C2). MANUAL + CHECK. BRECHA.
---

# sale-of-securities — Form 8949 (∉ retención 1446) (BRECHA)

> ⛔ **BRECHA (prioridad ALTA, pendientes v2.4).** Regla clave a documentar y verificar.

## Qué hace
Carga venta de acciones en **Form 8949** y asegura que las ganancias **no** entren a la
retención de Section 1446. Es un **módulo insertable** (Caso C2), no un return completo;
se compone dentro de C1/C3 cuando hay venta de securities.

## Depende de
- **source-resolver** → `sale.securities_1099b`.
- **cch-axcess-client**.

## Mapeo / reglas
- Data-entry 8949 (validado): description, fechas, costo, precio, 1099-B **code A**,
  short / long term.
- **Las ganancias short/long de acciones NO entran a Section 1446.** CCH las mete solo en
  el **8804 punto 4e**.
- Regla: **excluirlas** y verificar (ver cross-check-engine):
  - **Σ punto 9 del 8805 (socios foreign) = 4e del 8804**
  - **punto 10 = retención**

## Verificaciones (CHECK)
- securities ∉ 1446 (la verificación central de C2).

*(Fuente: video Form 8949 · doc pg23 "Form 8949", sección 09)*
