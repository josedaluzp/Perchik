---
name: cross-check-engine
description: Use after a 1065 return is populated in CCH Axcess to run the section-09 cross-checks before closing — ΣK-3 = K-2 = ΣK-1, securities ∉ 1446, 4797 = 1065 page 5, ownership % = 100, M-1/M-2 reconciliation. QA stage. CHECK.
---

# cross-check-engine — cruces de QA (sección 09)

## Qué hace
Cruza los números del return ya poblado, antes de cerrar. No corrige; **reporta**
discrepancias para que la skill responsable las arregle.

## Depende de
- **cch-axcess-client** (read) → lee los valores escritos.
- el return ya poblado (niveles 3–6).

## Cruces (sección 09)
| # | Verificación |
|---|--------------|
| 1 | **Σ K-3 = K-2 = Σ K-1** |
| 2 | **Securities ∉ 1446:** Σ punto 9 del 8805 = 4e del 8804 · punto 10 = retención |
| 3 | **Form 4797 = 1065 página 5** |
| 4 | Σ ownership % = 100% |
| 5 | M-1 / M-2 cuadran capital y net income |
| 6 | Cadena venta propiedad: 9c → 10 → 4m → 4q consistente |

## Salida
```yaml
checks:
  - id: k2_k3_k1
    pass: true
  - id: securities_not_1446
    pass: false
    detail: "4e del 8804 incluye 1,250 de securities; debería excluirlas"
all_pass: false
```

## Reglas
- Si algún check falla → no avanzar a print-efile; devolver a la skill responsable.
