---
name: foreign-forms
description: Use to populate the foreign-partner withholding and reporting forms for a 1065 in CCH Axcess — Form 8804 / 8805 plus the base K-2 / K-3. Computes the Section 1446 tax distinguishing corporate vs individual foreign partners. Stage 8. REGLA + CHECK.
---

# foreign-forms — 8804 / 8805 + K-2 / K-3 (etapa 8)

## Qué hace
Llena las formas de retención y reporte de socios foreign, y **calcula el §1446 tax**.

## Depende de
- **partners-k1** → quién es foreign, su tipo de entidad y su %.
- los **módulos de income** (incl. **sale-of-property** → 9c, 1231 gain).
- **cch-axcess-client**.

## ⚠️ §1446 tax — NO confundir el MONTO con el TAX
Error común: reportar la línea 4m (un monto base) como si fuera el impuesto. **El tax es el
resultado de aplicar las tasas.** La cuenta del Form 8804:

| Bucket | Quién | Línea 8804 | Tasa | → línea tax |
|--------|-------|-----------|------|-------------|
| ECTI ordinaria corporativa | socios **corp** | 4a | 21% | 5a |
| ECTI ordinaria no-corp | socios **individuos** | 4a/4e | 37% | 5a |
| Unrecaptured §1250 (de la venta) | **individuos** | **4m** | **25%** | **5d** |
| Adjusted net capital gain | **individuos** | **4q** | **20%** | **5e** |
| **TOTAL §1446 tax** | | **5f** = Σ 5a..5e | | **= línea 9 = línea 10** |

> El valor que se escribe como "§1446 tax" es **la línea 5f / 10**, no la 4m.

**Ejemplo real (AGGUILU 2025):** 4m = 342 → 5d = 342×25% = **86**; 4q = 16 → 5e = 16×20% =
**3**; **§1446 tax (5f/10) = 89**. (Reportar "342" como tax era el error.)

## Distinción CORP vs INDIVIDUAL (el corazón del caso C3)
- **Socio individuo:** sus ganancias preferenciales (9c → 4m, cap gain → 4q) se gravan
  **aunque su ECTI neta sea negativa** — los buckets de gain son separados de la pérdida
  ordinaria. Por eso el individuo **sí** paga 1446 sobre la venta.
- **Socio corporativo:** todo va a la ECTI corporativa (4a). Si la pérdida de actividad
  supera la ganancia → ECTI ≤ 0 → **0 de tax**.
- Resultado AGGUILU: los $89 son 100% del socio **individuo** (1%); el **corp** (99%) = $0.

## Por socio (Form 8805)
- **Línea 9** = ECTI allocable a ese socio. **Línea 10** = §1446 tax credit de ese socio.
- País del socio (country code) en el encabezado del 8805.
- **8804 = 0** entero cuando no hay ganancia y la ECTI total es ≤ 0 (Caso C1 / SALVIN7).

## K-2 / K-3 (US source vs Foreign source)
- income real estate → fila 2 ESI / US Source.
- expenses → punto 3 US Source.
- consulting foreign → columna Foreign.
- intereses → línea 6 (US vs Non-US).

## Securities ∉ 1446
Las ganancias de Form 8949 **no** entran a 1446: verificar Σ punto 9 del 8805 = 4e del 8804;
punto 10 = retención. (Coordinar con sale-of-securities.)

## Verificaciones (CHECK)
- **Σ línea 10 de todos los 8805 = línea 5f del 8804.**
- Socio corp con pérdida neta → su aporte al tax = 0.
- Σ K-3 = K-2 = Σ K-1.
