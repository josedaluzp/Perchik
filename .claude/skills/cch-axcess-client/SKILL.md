---
name: cch-axcess-client
description: Use when any 1065→CCH Axcess skill needs to WRITE data into CCH Axcess (Worksheets / Government Forms) or read back a field. The single sink — every skill writes through here. Mecanismo decidido (jun-2026): API oficial CCH Axcess Tax Services v2 — import/export XML por lotes, OAuth 2.0.
---

# cch-axcess-client — el sumidero (escribe en CCH Axcess)

> ✅ **Mecanismo DECIDIDO (jun-2026): API oficial — CCH Axcess Open Integration Platform,
> "Tax Services v2".** Modelo **por lotes, basado en archivos XML, asíncrono**. Se descarta la
> automatización de UI. El contrato lógico `write/read` no cambia para las demás skills, pero la
> implementación NO es campo-por-campo: se **acumula** (buffer) y se **vuelca** un XML de import
> por return.
>
> Portal/doc: https://developers.cchaxcess.com/ · Base URL:
> `https://api.cchaxcess.com/taxservices/oiptax/api/v1/`

## Qué hace

Único punto que toca CCH Axcess. Autentica (OAuth 2.0), **importa** datos a un return vía archivo
XML, y puede **exportar** el return para leer valores de vuelta (QA).

## Contrato lógico (estable — lo que ven las demás skills)

Las skills de núcleo/módulo NO arman XML ni llaman al API. Solo declaran valores lógicos:

**write (se acumula en el buffer del return, no viaja sola):**
```yaml
client: SALVIN7
field:
  form: "1065"
  worksheet: "Partner Information"
  line: "Ownership %"
  partner: "Partner 1"      # opcional, campos por socio
value: 50.0
```
**read:** mismo `field` → valor actual (sale del export del return). Para cross-check / diagnostic.

## Cómo lo implementa (modelo real Tax Services v2)

Flujo **buffer → flush → poll** por return:

1. **Identificar el return.** `Retrieve the list of returns` → ubicar el 1065 del cliente por
   `Client ID` + `Tax Year` + `Return Type` (+ `Return Version`/`ReturnId`). Si no existe la
   versión, `Create a new version of the provided return`.
2. **Acumular (buffer).** Recoger todos los `write` lógicos de las skills para ese return.
3. **Construir el XML de import** (formato "Tax Transfer", ver
   `references/tax-transfer-format.md`). Traducir cada dirección lógica:
   `worksheet`→`View Identifier Hierarchy`, sección→`WorkSheetSection Name`,
   `partner`→`Controls/Entity ID`, `line`+`value`→`FieldData Location`(FieldID)+`Value`.
   El XML va en UTF-16 → bytes → base64.
4. **Flush.** `POST …/ReturnsImportBatch` con `{ FileDataList:[base64], ConfigurationXml }`
   (`ImportMode=MatchAndUpdate` para socios repetidos) → devuelve `ExecutionID` (BatchGuid).
5. **Poll.** `GET …/BatchStatus?$filter=BatchGuid eq '<ExecutionID>'` hasta `Complete`
   (cada 1-2 min). Manejar `BIERR`/response codes (`RCRIU`=return in use).
6. **(opcional) Calcular.** `Submit a list of returns for calculation` (o `CalcReturnAfterImport`
   en el ConfigurationXml).
7. **read-back / QA.** `Submit a list of returns for export` → `BatchStatus` → `Stream the
   requested file` → parsear el XML exportado (mismo formato Tax Transfer).

Auth: header `Authorization: Bearer <access_token>` (OAuth 2.0). Un solo lugar con el token,
el refresh y el manejo de errores de CCH.

## Pendiente de detalle (antes de codificar)

El **formato ya está resuelto** (ver `references/tax-transfer-format.md`). Falta:

1. **Field codes del 1065** ⬅️ *lo único crítico.* El ejemplo de la API es Individual
   (`ReturnType="I"`, codes `IFDSGEN.*`); el 1065 es **Partnership (`ReturnType="P"`)** con otros
   codes. Obtenerlos: (a) **Tax Transfer User Guide** (Tax help files de CCH), o (b) **exportar un
   1065 terminado** (AGGUILU/SALVIN7, ya disponibles como `reference.finished_1065`) → el export
   trae los `Location` reales de cada campo. **Vía (b) es la más directa.**
2. **OAuth 2.0:** `client_id`/`secret` de integrador, token endpoint, scopes, ¿sandbox?
3. **Licencia:** v2 avisa "Some operations require additional licensing" — confirmar import.

## Operaciones hermanas (NO las consume esta skill, pero existen)
- **print-efile:** `Submit a list of returns for print`, y e-file: release candidates,
  upload-and-hold, `Retrieve the status of the e-filed returns`.
- **roll forward:** `Submit a list of returns to roll forward` (año siguiente).
- **status:** `Update the return status of the provided list of returns`,
  `Update the return description`, `Unlock Return`.

## Por qué un solo sumidero
- Una sola auth, un solo armado de XML, un solo manejo de batch/errores de CCH.
- Las skills quedan testeables con un mock del contrato lógico aunque el XML real evolucione.
- El modelo por lotes encaja con el pipeline: cada return se vuelca en 1 import, no en N llamadas.
