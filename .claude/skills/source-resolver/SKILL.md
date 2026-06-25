---
name: source-resolver
description: Use when any 1065→CCH Axcess skill needs to locate a piece of source data for a client — answers "where does datum X for client Y live?" and returns the connector (Airtable/Dropbox) plus the exact locator. The single place that knows the geography of the data. Do not hardcode folder paths or Airtable IDs in other skills; ask the resolver.
---

# source-resolver — el diccionario de fuentes

## Qué resuelve

Es la **bisagra** entre los conectores tontos (MCP Airtable / Dropbox) y las skills que
interpretan datos. Su único trabajo: dado un **dato lógico** (`logical_key`) y un
**cliente**, responder **dónde está** ese dato.

No descarga ni interpreta nada. Solo dice: *"el Operating Agreement de SALVIN7 está en
Dropbox, en esta carpeta"* o *"el % de cada socio está en Airtable, base X, tabla Y"*.

```
skill ──pregunta──►  source-resolver  ──responde──►  { connector, locator }
                          │ (lee el diccionario)
skill ──con el locator──► conector (MCP)  ──►  bytes / records
skill interpreta y escribe en CCH
```

## Contrato

**Entrada:**
- `logical_key` — clave del dato lógico (ej. `entity.operating_agreement`,
  `partners.ownership_pct`, `income.qb_profit_and_loss`). Lista completa en
  `references/sources.yaml`.
- `client` — identificador del cliente (nombre de entidad / ID de Airtable).

**Salida:**
```yaml
connector: dropbox            # o airtable
locator:                      # forma según el connector (ver abajo)
  path: "/Clients/SALVIN7/Formation/"   # dropbox
  match: "*Operating Agreement*.pdf"
notes: "Si hay varias versiones, tomar la más reciente."
found: true                   # false si el dato no aplica a este escenario
```

**Formas de `locator`:**
- **dropbox** → `{ search_scope, name_contains, match, prefer }`. Se **localiza por search**
  dentro de `Clients`, no por path fijo: la ruta real es
  `Clients/Tax Clients/{owner}/{entity}/{year}/` y `{owner}` es una capa variable, así que
  construir el path es frágil. Se busca por nombre de entidad + patrón de archivo y se toma
  el año más reciente.
- **airtable** → `{ table, match_name | match_via, fields }`.

## Cómo trabaja

1. Carga el diccionario `references/sources.yaml`.
2. Busca la entrada cuyo `key` == `logical_key`.
3. Resuelve los placeholders de cliente (`{client}`) contra la convención del conector
   (carpeta raíz de Dropbox, base de Airtable — definidos en el header del YAML).
4. Devuelve `{ connector, locator, notes }`. Si la key no existe → error claro
   listando las keys disponibles. Si la key existe pero no aplica al escenario →
   `found: false`.

**El resolver nunca llama al conector.** Solo arma la dirección. Quien pidió el dato es
quien luego invoca el MCP de Airtable/Dropbox con ese locator.

## Cómo agregar / cambiar una fuente

Editar **solo** `references/sources.yaml`. Cada entrada:

```yaml
- key: entity.operating_agreement
  needed_by: [basic-data, ownership-structure, partners-k1]
  connector: dropbox
  locator:
    path: "{dropbox_root}/{client}/Formation/"
    match: "*Operating Agreement*.pdf"
  notes: "Define socios, %, y representante. Tomar la versión firmada más reciente."
```

## Errores comunes

- **Hardcodear una ruta en otra skill.** Si una skill conoce un path de Dropbox, está mal:
  ese conocimiento va aquí.
- **Hacer que el resolver descargue o parsee.** Fuera de alcance — eso es del conector
  (traer) y de `qb-report-reader` / la skill consumidora (interpretar).
- **Inventar un `logical_key`.** Si falta un dato, primero agregarlo a `sources.yaml`.
- **Meter IDs de Airtable o roots de Dropbox repartidos.** Van una sola vez, en el header
  del YAML (`connectors:`).
