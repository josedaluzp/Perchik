---
name: return-orchestrator
description: Use whenever the user asks to prepare / draft / map / "armar" a Form 1065 for a client in CCH Axcess — triggers on short phrases like "armá el 1065 de X", "prepará el 1065 de X", "borrador 1065 X", "data-entry de X", "mapeá X a CCH". Runs the whole read-only pipeline end-to-end and returns the filled-form mockup. The user does NOT need to name the individual skills.
---

# return-orchestrator — armar el 1065 de un cliente (end-to-end)

> **Activación corta.** Si el usuario dice *"armá / prepará / hacé el 1065 de **[CLIENTE]**"*
> (o variantes), corré TODO esto sin pedirle que liste skills ni pasos. Lo único que necesitás
> es el **nombre del cliente**; si no lo dio, preguntalo y nada más.

## Qué hace
Toma un cliente y produce el **borrador del Form 1065 mapeado a CCH Axcess**, en modo
**solo lectura** (nunca escribe en CCH). Salida por defecto: un **artifact HTML** con las
tablas por worksheet (Campo · Valor · Fuente · Estado) y el contador de automatización.

## Procedimiento (automático)
1. **Clasificar** (`scenario-classifier`): leer el registro de la entidad en Airtable y detectar
   flags — real estate, consulting, holding/K-1 recibidos, venta de propiedad, venta de
   securities, cambio accionario, socios foreign. Eso define qué módulos correr.
2. **Localizar + traer** (`source-resolver` + conectores MCP):
   - Airtable → entidad (Entity Tracker) y socios (Individual Tracker).
   - Dropbox → P&L, Balance Sheet, Capital Account, depreciation/Property List, HUDs, K-1
     recibidos, 1099, según los flags.
   - Si existe `reference.finished_1065`, leerlo como **ground truth** para validar.
3. **Mapear** corriendo las skills de núcleo + los módulos de income que correspondan:
   `basic-data`, `other-information`, `ownership-structure`, `efile-config`, `partners-k1`,
   `income-router` → módulo(s), `balance-sheet`, `foreign-forms`.
4. **QA** (`cross-check-engine`, `diagnostic-runner`): correr los cruces y marcar lo que no cierra.
5. **Devolver el mockup** (formato estándar, abajo). **No** ejecutar `print-efile` ni escribir
   en CCH — el cierre real es manual hasta que exista `cch-axcess-client`.

## Resultado hacia intake-trigger
Cuando lo invoca `intake-trigger` (flujo automático), además del mockup hay que devolver un
**resultado explícito** para que el trigger sepa qué estado escribir en Airtable:
- **`success`** → el borrador + mockup se generaron (aunque haya campos en CHECK/MANUAL: eso es
  normal y queda para revisión humana). → el trigger marca `CCH Ready to Check`.
- **`failure`** → no se pudo armar el borrador: falta una fuente crítica (P&L, socios, etc.),
  no se localizó la carpeta del cliente, o hubo una excepción. Devolver el **motivo**. → el
  trigger marca `CCH Corregir`. Nunca devolver `success` si el borrador quedó incompleto por
  falta de datos base.

## Salida hacia completion-report

Además del mockup, cuando corre en flujo automático el orquestador expone un objeto que
`completion-report` consume para armar el mail (no re-calcula nada):

```yaml
client: AGGUILU LLC
result: success            # success | failure
reason: null               # motivo, solo si failure
mockup: "file:///C:/Users/PC/Downloads/1065_AGGUILU_mockup.html"
fields_by_status:          # derivado de los estados del mockup (AUTO/REGLA/CHECK/MANUAL)
  auto:   [ "<worksheet · línea>" ]   # cargados directo de la fuente
  regla:  [ "<worksheet · línea>" ]   # derivados por regla fiscal
  check:  [ "<worksheet · línea>" ]   # resueltos pero a verificar por una persona
  manual: [ "<worksheet · línea>" ]   # no están en las fuentes → carga humana
  missing:[ "<dato/fuente faltante>" ]
qa:
  cross_checks: "resumen de cross-check-engine"
  diagnostics:  "resumen de diagnostic-runner"
cch_upload: pending        # done | pending (pending mientras cch-axcess-client esté gated)
```

Los valores de `fields_by_status` salen del contador y las filas del mockup (columna Estado);
no es información nueva, es el mismo mockup en forma estructurada.

## Formato de salida (mockup estándar)
Artifact HTML con:
- Cabecera del return (nombre, EIN, año, método, actividad, socios).
- **Contador de automatización** arriba: % = (AUTO + REGLA) / total de campos.
- Una tarjeta por worksheet con tabla **Campo · Valor · Fuente · Estado**.
- **Estados:** `AUTO` (directo de la fuente) · `REGLA` (derivado por regla fiscal) ·
  `CHECK` (resuelto pero verificar) · `MANUAL` (no está en las fuentes).

## CHECK que SIEMPRE hay que marcar
- **Dirección:** comparar la de Airtable contra la del 1065/SS-4 (suele estar desactualizada en Airtable).
- **% de socios:** no sale del Capital Account de QB (cuenta única "Member") → viene del
  Schedule B-1 / Operating Agreement. Marcar para verificar.
- **9c (§1250):** es la depreciación ACUMULADA de los edificios vendidos, no la del año (ver sale-of-property).
- **§1446 tax:** es la línea 5f del 8804, no la 4m (ver foreign-forms).
- **Fair Rental Days:** no surge del P&L → MANUAL.
- **Balance suprimido:** si está bajo umbral, igual cargar buildings/land + amortización.

## Reglas
- Modo lectura: jamás escribir en CCH Axcess.
- Mismo esqueleto para todos los casos; cambia qué enciende `income-router` y cómo se
  configura `foreign-forms`.
- Si falta un dato fuente, marcarlo (CHECK/MANUAL) en vez de inventarlo.
