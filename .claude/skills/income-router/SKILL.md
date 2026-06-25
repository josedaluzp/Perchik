---
name: income-router
description: Use to dispatch a 1065 return to the correct income module(s) based on the scenario-classifier flags. Stage 6 — the only node that branches the tree. Runs one or more of the 7 income modules; enters no data itself.
---

# income-router — despacho de income (etapa 6, ramifica)

## Qué hace
Único nodo que abre el árbol: según los flags de **scenario-classifier**, decide qué
módulo(s) de income correr. No entra data; solo despacha.

## Depende de
- **scenario-classifier** → los flags / `income_modules`.

## Tabla de despacho
| Flag / actividad | Módulo |
|------------------|--------|
| real_estate | income-real-estate |
| consulting (USA) | income-consulting-usa |
| consulting (foreign) | income-consulting-foreign |
| receives_k1 (holding) | income-passthrough-k1 |
| sale_of_property | sale-of-property |
| sale_of_securities | sale-of-securities |
| change_in_ownership | change-in-ownership |

## Reglas
- Puede encender **varios** módulos (ej. C3: income-real-estate + sale-of-property).
- Los módulos son hermanos independientes; el router no impone orden entre ellos.
- Si ningún flag aplica → marcar para revisión manual (no inventar income).
