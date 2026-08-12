---
name: sale-of-securities
description: Use to enter a sale of securities (stocks) for a 1065 in CCH Axcess via Form 8949 — short/long-term gains must be verified to stay excluded from Section 1446 withholding (CCH does not exclude them automatically). An insertable income module (Case C2). REGLA + CHECK.
---

# sale-of-securities — Form 8949 (∉ retención 1446)

## Qué hace
Carga venta de acciones en **Form 8949** y verifica que las ganancias **no** queden gravadas
por la retención de Section 1446. Es un **módulo insertable** (Caso C2), no un return
completo; se compone dentro de C1/C3 cuando hay venta de securities.

## Depende de
- **source-resolver** → `sale.securities_1099b`.
- **cch-axcess-client**.

## 1. Carga por venta, una fila por vez
`Income › Schedule D, 4797, Gain and Loss › Detail` — una fila por cada venta. Por cada
venta, copiar del 1099-B:
- Descripción (idéntica al 1099-B).
- Fecha de adquisición y fecha de venta.
- Precio de venta y costo.
- `1099-B Code = A`.
- Short/long term (> 1 año en la posición = long term).

## 2. Cross-check contra la fuente
El total cargado en Schedule D/8949 debe coincidir exacto (o con diferencia de redondeo ≤ $1)
con el total del 1099-B de origen.

## 3. La exclusión de Section 1446 NO es automática — es una verificación manual
Error a evitar: pensar que hay algo que "configurar" para excluir la ganancia. **CCH carga la
ganancia short/long-term en el 8804 línea 4e y en la retención por default**, igual que si
fuera income gravado. La regla operativa:
- Sumar el punto 9 de **todos** los 8805 de socios foreign → debe dar igual a la línea **4e**
  del 8804 (tolerancia ~$1 por redondeo).
- Sumar el punto 10 (retención) de todos los 8805 → debe dar igual a la retención total.
- **Si no cierra:** no ajustar montos a mano en el 8949 ni forzar el 8804/8805 — es señal de
  que hay otro income mezclado en el 4e (o falta un socio en el 8805). Flaggear para revisión
  manual.

## Verificaciones (CHECK)
- securities ∉ 1446 (regla 3, la verificación central de C2).
- Total 8949 == total 1099-B (regla 2).

*(Fuente: `trancript/form-8949/part1.txt`.)*
