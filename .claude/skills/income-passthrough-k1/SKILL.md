---
name: income-passthrough-k1
description: Use when a 1065 entity is a holding that RECEIVES K-1s from other partnerships — loads each received K-1 line by line into Income › Partnership Passthrough (K-1 1065). An income module dispatched by income-router. MANUAL. BRECHA — needs its own rule defined.
---

# income-passthrough-k1 — holding que recibe K-1 (BRECHA)

> ⛔ **BRECHA (prioridad ALTA, pendientes v2.4).** En v2.3 esto quedaba como 1 línea MANUAL
> fuera de R1 y el doc admite que "Holding necesita regla propia". Aquí se define.

## Qué hace
Carga el income de una **holding** que recibe K-1 de otras sociedades, **línea por línea**,
en `Income › Partnership Passthrough (K-1 1065)`.

## Depende de
- **source-resolver** → `income.k1_received`.
- **cch-axcess-client**.

## Mapeo / reglas (a formalizar)
- Por cada K-1 recibido: cargar cada renglón (ordinary income, rental, interest, etc.) en su
  línea de Partnership Passthrough.
- Caso C1 (SALVIN7): su income entra por **3 K-1 recibidos**.
- Coordinar con foreign-forms y K-2/K-3 (qué es US source vs Foreign source).

## Pendiente de definir
- Regla propia de mapeo renglón-K-1 → línea CCH (la "regla propia" que pide v2.3).
- Cómo se agrega/concilia con el resto del income de la holding.

*(Fuente: video SALVIN7 PI 12:00-15:00 · doc pg22-23, pg50)*
