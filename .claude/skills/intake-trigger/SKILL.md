---
name: intake-trigger
description: Use to detect that a 1065 return is ready to process — watches Airtable for an entity whose "Primary Form Status" = "CCH To do" and kicks off the return-orchestrator for that client. The entry point of the whole pipeline.
---

# intake-trigger — el disparo

## Qué hace

Escucha el disparo en Airtable y arranca el pipeline para un cliente.

**Condición de disparo:** `entities."Primary Form Status" == "CCH To do"`.

## Depende de
- **source-resolver** → `entity.record` (define base/tabla/campo del trigger).
- **airtable-connector (MCP)** → para leer el estado.

## Procedimiento
1. Resolver la dirección del trigger vía source-resolver (header `connectors.airtable.trigger`).
2. Buscar entidades con `Primary Form Status = "CCH To do"`.
3. Por cada una, invocar **return-orchestrator** con `client = <entidad>`.
4. (Opcional) marcar la entidad como "en proceso" para no re-disparar.

## Salida
```yaml
triggered:
  - client: SALVIN7
  - client: AGGUILU
```

## Reglas
- Idempotente: no disparar dos veces el mismo cliente en el mismo estado.
- No clasifica ni mapea nada — solo detecta y delega. La clasificación es de
  scenario-classifier.
