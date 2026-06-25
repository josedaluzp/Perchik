---
name: partners-k1
description: Use to populate Partner Information for a 1065 in CCH Axcess — each partner's ownership %, capital accounts, entity type (individual vs corp), and TIN/SSN rules. Stage 5. AUTO + REGLA + CHECK. Drives the K-1/K-3 print config.
---

# partners-k1 — Partner Information (etapa 5)

## Qué hace
Carga la info de cada socio: %, cuentas de capital, tipo de entidad, identificación.

## Depende de
- **source-resolver** → `partners.list`, `entity.operating_agreement`.
- **cch-axcess-client** → escribe.

## Mapeo / reglas
| Dato | Regla |
|------|-------|
| Ownership % | de partners.list / OA |
| Capital accounts | de partners.list / OA |
| **Entity type** (individual vs corp) | crítico: define camino en 8804 (ver foreign-forms) |
| **TIN/SSN del socio sin número** | a verificar regla (ver abajo) |
| K-1/K-3 Print | produce for all partners · suppress state · also in client copy |

## Verificaciones (CHECK)
- Σ ownership % == 100%.
- Tipo de entidad consistente con foreign-forms (corp foreign vs individual foreign).

## A verificar (de pendientes v2.4)
- **Regla TIN/SSN:** v2.3 la redacta por tipo de actividad (consulting-foreign/loss →
  `888-00-8888`; real estate con ganancia → `APPLIED FOR`). Pero en SALVIN7 y AGGUILU el
  socio **corp foreign** se cargó como **"Applied for"** en ambos. → ¿La regla en realidad
  depende del **tipo de entidad** (corp → Applied for)? Confirmar y reescribir aquí.

## Brechas (de pendientes v2.4)
- K-1/K-3 Print en el escenario estándar (en v2.3 solo estaba en Escenario C).
