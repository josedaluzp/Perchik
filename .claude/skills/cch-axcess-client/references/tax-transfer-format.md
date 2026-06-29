# CCH Axcess Tax Services v2 — formato real de import/export ("Tax Transfer")

Descubierto jun-2026 desde https://developers.cchaxcess.com/ (Tax Services v2).
Esta es la referencia técnica que implementa `cch-axcess-client`.

## Endpoint de import (escritura)

`POST https://api.cchaxcess.com/taxservices/oiptax/api/v1/ReturnsImportBatch`

A.k.a. **"Tax Transfer"**: toma datos en XML y puebla los *worksheet inputs* del return.
Soporta cualquier input que permita entrada manual; todos los tipos de return y autoridades
(federal/state/city). Los records repetidos (p.ej. socios) se pueden **matchear y actualizar**
según criterios de matching (ver Tax Transfer User Guide en los Tax help files de CCH).

Headers: `Authorization: Bearer <oauth2_token>` (recomendado).

### Request body (`ImportRequest`, application/json)
```json
{
  "FileDataList": ["<base64 del XML de Payload, codificado en UTF-16>"],
  "ConfigurationXml": "<TaxDataImportOptions>...</TaxDataImportOptions>"
}
```
- **FileDataList**: lista de archivos; cada uno es el XML `Payload` (abajo) → bytes UTF-16 → base64.
  Un elemento por return. (En .NET el ejemplo es `Encoding.Unicode.GetBytes(xml)` → `Convert.ToBase64String`.)
- **ConfigurationXml**: opciones del import (abajo).

### Response (`IXResponse`)
```json
{ "ExecutionID": "<BatchGuid>", "FileResults": [ { "FileGroupID": 1, "IsError": false,
  "Messages": ["Successfully submitted"], "SubItemExecutionIDs": ["<item guid>"] } ] }
```
- **ExecutionID** = el **BatchGuid** que se usa para pollear estado.
- **SubItemExecutionID** = guid por archivo cuando se mandan varios en una llamada.

## Poll de estado (asíncrono)

`GET …/api/v1/BatchStatus?$filter=BatchGuid eq '<ExecutionID>'`
(agregar `and Expand eq 'Items'` para detalle por ítem). Chequear cada 1-2 min (import/export
son rápidos). Estados batch: `BAINS/BASCH/BARTR/BAINP/BASTG/BASTD/BACMP/BAEXC/BATRD`
(`Complete` cuando corresponde). Ítems: `BIUNP/BIINP/BIPCD/…/BIERR/BICMP`. Response codes
relevantes: `RCS`=Succeeded, `RCRIU`=Return in use, etc.

## ConfigurationXml (opciones de import)
```xml
<TaxDataImportOptions>
  <ImportMode>MatchAndUpdate</ImportMode>            <!-- match de records repetidos (socios) -->
  <CaseSensitiveMatching>false</CaseSensitiveMatching>
  <InvalidContentErrorHandling>RejectReturnOnAnyError</InvalidContentErrorHandling>
  <CalcReturnAfterImport>false</CalcReturnAfterImport>
</TaxDataImportOptions>
```

## Payload XML (el archivo de datos) — EJEMPLO REAL decodificado
```xml
<?xml version="1.0" encoding="utf-16"?>
<Payload DataType="Tax" DataFormat="Standard" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <TaxReturn>
    <ReturnHeader ClientID="JOHNDOE" TaxYear="2021" ReturnType="I" ReturnGroupName="Default"
                  Country="US" OfficeName="Dallas" BusinessUnitName="Development"
                  ConfigurationSet="Default" ReturnVersion="1" EINorSSN="123-45-6789"
                  ControlNumber="202204290404471817" />
    <TaxPayerDetails NameLine1="JOHN" NameLine2="DOE" />
    <View xsi:type="Worksheet">
      <Identifier Hierarchy="Federal\General\Basic Data" />
      <Controls>
        <Entity ID="1" />
      </Controls>
      <WorkSheetSection Name="General">
        <FieldData Location="IFDSGEN.0"  LocationType="FieldID" Value="TX" />
        <FieldData Location="IFDSGEN.2"  LocationType="FieldID" Value="Head of household" />
        <FieldData Location="IFDSGEN.41" LocationType="FieldID" Value="JOHN" />
        <FieldData Location="IFDSGEN.43" LocationType="FieldID" Value="DOE" />
        <FieldData Location="IFDSGEN.5"  LocationType="FieldID" Value="123-45-6789" />
      </WorkSheetSection>
    </View>
  </TaxReturn>
</Payload>
```

## Mapeo al contrato lógico de cch-axcess-client
| Contrato lógico        | XML Tax Transfer                                  |
|------------------------|---------------------------------------------------|
| `field.worksheet`      | `View > Identifier Hierarchy` (ej. `Federal\General\Basic Data`) |
| sección                | `WorkSheetSection Name`                           |
| `field.partner`        | `Controls > Entity ID` (instancia del record repetido) |
| `field.line` + `value` | `FieldData Location` (FieldID) + `Value`          |

## OJO — esto es Individual; nuestro caso es 1065 (Partnership)
- El ejemplo es `ReturnType="I"` (Individual). **El 1065 es Partnership → `ReturnType="P"`**
  (confirmar el código exacto). El return id del ejemplo es `2021I:Individual:V1`; para socios
  sería del estilo `2025P:Partnership:V1`.
- Los **field codes** (`IFDSGEN.0`, …) son específicos de Individual. Los del **1065 son
  distintos** (otro prefijo). Dos formas de obtenerlos:
  1. **Tax Transfer User Guide** (Tax help files de CCH) — el catálogo oficial de field codes.
  2. **Exportar un 1065 ya terminado** (`Submit a list of returns for export` → descargar XML):
     el export devuelve el MISMO formato con los `Location` poblados → de ahí salen los field
     codes reales de cada worksheet/línea que nos importa. Encaja con `reference.finished_1065`
     (ya tenemos returns terminados de AGGUILU/SALVIN7 como ground truth).

## Identificación del return (ReturnHeader)
Claves: `ClientID`, `TaxYear`, `ReturnType`, `ReturnVersion` (+ `ReturnGroupName`,
`ConfigurationSet`, `OfficeName`, `BusinessUnitName`, `EINorSSN`, `ControlNumber`).
Descubrir returns existentes: `Retrieve the list of returns`. Si no existe la versión:
`Create a new version of the provided return`.
```
