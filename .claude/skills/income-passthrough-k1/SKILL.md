---
name: income-passthrough-k1
description: Use when a 1065 entity is a holding that RECEIVES K-1s from other partnerships — loads each received K-1 line by line into Income › Partnership Passthrough (K-1 1065), aggregates real estate and interest into K-2 Section 10 (US Source), and excludes non-deductible expenses from K-2/K-3. An income module dispatched by income-router. REGLA + CHECK.
---

# income-passthrough-k1 — holding que recibe K-1

## Qué hace
Carga el income de una **holding** que recibe K-1 de otras sociedades, **línea por línea**,
en `Income › Partnership Passthrough (K-1 1065)`, y agrega el resultado al K-2/8804 de la
sociedad. No cubre la actividad propia de la holding (eso lo maneja el módulo de income que
corresponda, ej. income-consulting-foreign) — income-router enciende ambos en paralelo cuando
aplica.

## Depende de
- **source-resolver** → `income.k1_received`.
- **cch-axcess-client**.
- Coordina con **income-consulting-foreign** (o el módulo de actividad propia que dispare
  income-router) y con **balance-sheet**.

## 1. Carga por K-1, campo por campo
Por cada K-1 recibido: abrir `Income › Partnership Passthrough (K-1 1065)`, completar:
- Nombre de la sociedad emisora, tipo (domestic/limited), % de participación.
- Partner Capital Account Analysis.
- Cada casilla del K-1 real (net rental real estate income/loss, interest, deductions,
  non-deductible expenses, business interest expense, current year gross receipts, etc.) se
  tipea **1 a 1** en el campo del mismo nombre del worksheet — sin cálculo, transcripción
  directa.

*(Caso SALVIN7: 3 K-1 recibidos — Airport Crossing Investors, Cherokee Investors, Rose
Investors.)*

## 2. Agregación al K-2, Section 10 (US Source)
Asume que las sociedades emisoras de los K-1 recibidos son domésticas:

- **Línea 6 (Interest):** sumar el interest (box 5) de todos los K-1 recibidos → columna
  US Source. *(SALVIN7: 72 + 122 + 257 = 451.)*
- **Real estate (income o deductions según signo):** sumar el "net rental real estate
  income/loss" (box 2) de todos los K-1.
  - Si el neto es **positivo** → línea de INCOME correspondiente, columna US Source.
  - Si el neto es **negativo** → línea de DEDUCTIONS, columna US Source, sumándole el total
    de "Deductions" (box 13) de esos mismos K-1.
  *(SALVIN7: neto = −6.138 − 6.285 + 0 = −12.423; + (47+32+49) = **12.551**.)*

## 3. Excluir del K-2/K-3 los "non-deductible expenses"
Los non-deductible expenses de los K-1 recibidos bajan el capital account del socio en **su
propio** K-1, pero **no** deben cargarse en el K-2/K-3 de los socios de la sociedad que los
recibe.

## 4. Balance sheet
El ending capital account de cada K-1 recibido (Partner Capital Account Analysis, línea
final) se carga como inversión/"Other Asset" en el balance — una línea por cada sociedad de
la que se recibe K-1.

## 5. 8804
Solo entra la porción US-source (el resultado agregado de los K-1 recibidos, si es positivo)
prorrateada al socio corp según su %. La actividad foreign propia de la holding **nunca**
toca el 8804. *(SALVIN7: resultado negativo → 8804 en cero.)*

## Verificaciones (CHECK)
- **K-2 total == P&L net income**, con diferencia tolerada únicamente por los non-deductible
  expenses excluidos (regla 3). Diferencia mayor → no forzar el cierre, flaggear para revisión
  manual (`cross-check-engine`).
- **Σ ending capital account de todos los socios (K-1) == balance sheet "Partners' capital
  accounts"** al cierre. Si no cierra → revisión manual antes de imprimir.
- Si algún K-1 da ganancia real estate positiva y hay socio corp con % > 0 → confirmar
  explícitamente que impacta el 8804 línea 4a (no asumir 0).

*(Fuente: `trancript/salvin7-llc-consulting-fuera-de-usa/part1.txt`, `part2.txt`, `part3.txt`.)*
