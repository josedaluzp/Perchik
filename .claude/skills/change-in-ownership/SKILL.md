---
name: change-in-ownership
description: Use when a 1065 has a change in ownership (cambio accionario) — files AMENDED return and prorates by days. An income module dispatched by income-router. REGLA.
---

# change-in-ownership — cambio accionario (AMENDED + prorrateo)

## Qué hace
Maneja el escenario de cambio de socios durante el año.

## Depende de
- **source-resolver** → `partners.list`, `entity.operating_agreement`.
- **cch-axcess-client**.

## Mapeo / reglas
- Marcar return como **AMENDED**.
- **Prorrateo por días** de cada socio según fechas de entrada/salida.
- Coordinar con partners-k1 (capital accounts) y balance-sheet (M-2, Escenario C).
- K-1/K-3 Print: produce for all partners · suppress state · also in client copy.

## Notas
- Escenario C del doc v2.3.
