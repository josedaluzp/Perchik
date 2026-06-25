---
name: ownership-structure
description: Use to populate Schedule B-1 and the Partnership Representative in CCH Axcess for a 1065 — who owns the partnership and who represents it. Stage 3. REGLA.
---

# ownership-structure — Schedule B-1 + Partnership Representative (etapa 3)

## Qué hace
Carga la estructura de propiedad (Sch B-1) y designa al Partnership Representative.

## Depende de
- **source-resolver** → `entity.operating_agreement`, `partners.list`.
- **cch-axcess-client** → escribe.

## Mapeo / reglas
- **Sch B-1:** socios con ≥ 50% (o según umbral del form) desde el OA / partners.list.
- **Partnership Representative:** del OA. Si es entidad, requiere designado individual.

## Verificaciones
- Σ de % de propiedad == 100%.
- El representante existe como socio o designado válido.

## Notas
- Comparte fuente (OA) con partners-k1; ambos piden `entity.operating_agreement` al resolver,
  no se pasan el dato entre sí.
