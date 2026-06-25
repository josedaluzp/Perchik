---
name: scenario-classifier
description: Use at the start of a 1065 return to detect the entity's activity and flags (foreign, real estate, holding, sale of property, sale of securities, change in ownership) so the orchestrator knows which income modules and foreign-forms config to run. Decides the path; does not enter any data.
---

# scenario-classifier — define el camino

## Qué hace

Lee la entidad y determina **qué escenario** es, devolviendo flags que el
return-orchestrator y el income-router usan para decidir qué skills correr.

## Depende de
- **source-resolver** → `entity.record` (flags en Airtable) y, si hace falta, OA / reportes.
- **airtable-connector (MCP)**.

## Salida
```yaml
client: SALVIN7
activity: consulting          # real_estate | consulting | holding | mixed
flags:
  foreign_partners: true
  receives_k1: true           # holding que recibe K-1 → income-passthrough-k1
  sale_of_property: false
  sale_of_securities: false
  change_in_ownership: false
income_modules:               # qué encenderá el income-router
  - income-consulting-foreign
  - income-passthrough-k1
foreign_forms: { needed: true, mode: "8804=0" }
```

## Cómo decide (heurística)
- **foreign_partners** → si algún socio es foreign (partners.list) → activa foreign-forms.
- **receives_k1** → si hay K-1 recibidos (holding) → income-passthrough-k1.
- **real_estate** → activa income-real-estate (+ sale-of-property si hay HUD).
- **sale_of_securities** → si hay 1099-B → sale-of-securities (∉ retención 1446).
- **change_in_ownership** → si hay cambio accionario → AMENDED + prorrateo.

## Los 3 casos de referencia
- **C1 · SALVIN7:** consulting foreign + recibe K-1 + socios foreign.
- **C2 · Form 8949:** venta de securities (módulo insertable, no return completo).
- **C3 · AGGUILU:** real estate con socio corp + venta de propiedades.

## Reglas
- Solo clasifica. No entra data en CCH.
- Si los flags de Airtable y la evidencia documental (OA, reportes) se contradicen,
  marcar `needs_review: true` en vez de adivinar.
