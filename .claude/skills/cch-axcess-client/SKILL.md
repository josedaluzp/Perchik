---
name: cch-axcess-client
description: Use when any 1065→CCH Axcess skill needs to WRITE data into CCH Axcess (Worksheets / Government Forms) or read back a field. The single sink — every skill writes through here. Mecanismo decidido (jun-2026): API oficial CCH Axcess Tax Services v2 (OAuth 2.0).
---

# cch-axcess-client — el sumidero (escribe en CCH Axcess)

> ✅ **Mecanismo DECIDIDO (jun-2026): API oficial — CCH Axcess Open Integration Platform,
> "Tax Services v2"** (*"Import and export data to tax returns"*; v1 también lo hace pero v2 es
> la recomendada). Se **descarta la automatización de UI**. El **contrato** `write/read` de abajo
> NO cambia: se implementa traduciendo la dirección lógica del campo a la operación de
> import/export del API. Quedan por detallar el endpoint exacto, el schema de import y los
> field codes (ver "Implementación — pendiente de detalle").
>
> Acceso al portal: https://developers.cchaxcess.com/ (login CCH Axcess / WK).

## Qué hace

Único punto que toca CCH Axcess. Autentica y **escribe** valores en campos de
Worksheets / Government Forms, y puede **leer** un campo de vuelta (para QA).

## Contrato (estable, independiente del mecanismo)

**write:**
```yaml
client: SALVIN7
field:                      # dirección lógica del campo en CCH
  form: "1065"
  worksheet: "Partner Information"
  line: "Ownership %"
  partner: "Partner 1"      # opcional, para campos por socio
value: 50.0
```
**read:** mismo `field` → devuelve el valor actual (para cross-check / diagnostic).

Toda skill de núcleo/módulo escribe **solo** a través de este contrato. Nunca tocan CCH
por su cuenta.

## Implementación — pendiente de detalle (camino API confirmado)

Mecanismo = **Tax Services v2** (OIP). Falta extraer de la doc del portal, antes de codificar:

1. **Auth (OAuth 2.0):** flujo recomendado por WK. Cómo se obtienen `client_id`/`secret` de
   integrador, endpoint de token, scopes. ¿Hay entorno **sandbox/test** separado de producción?
2. **Identificar el return:** cómo se referencia un 1065 concreto (client id + tax year + return
   id / version). Hay endpoint de **return listings** para descubrirlos.
3. **Mecanismo de escritura:** la API "importa/exporta datos al return". Confirmar si el import
   es **por lote/payload estructurado** (probable) y cuál es su **schema** + el sistema de
   **field codes** de CCH (cómo se nombra "Partner Information › Ownership %" en el import).
   El contrato lógico de abajo se traduce a esos field codes acá.
4. **Licencia:** v2 dice *"Some operations require additional licensing"* — confirmar que la
   operación de **import** está habilitada en la licencia del estudio.
5. **read-back:** usar el **export** del mismo API para leer un campo (QA / cross-check).

> Nota: APIs hermanas relevantes para otras skills — **Tax Return eFile Status** (print-efile),
> **Staff/signers** (efile-config), **Client** (alta de entidad). No las consume esta skill.

## Por qué un solo sumidero
- Un solo lugar con la auth y el manejo de errores de CCH.
- Las skills quedan testeables con un mock de este contrato aunque el mecanismo real
  todavía no exista.
