# cch-axcess-mcp — design

## Contexto

`cch-axcess-client` (ver `.claude/skills/cch-axcess-client/SKILL.md`) es "el
sumidero": el único punto de la arquitectura de skills que escribe/lee datos
reales en CCH Axcess. Las demás 24 skills (ya cargadas en Claude Desktop)
solo declaran valores lógicos (`write: {form, worksheet, line, partner,
value}`) — no saben armar XML ni llamar a una API.

Ese contrato lógico necesita algo que lo ejecute de verdad: autenticar
contra CCH (OAuth 2.0), armar el XML "Tax Transfer", postearlo, y pollear el
resultado. Eso es `cch-axcess-mcp`: un servidor **MCP por stdio** que
Claude Desktop invoca como un tool más (mismo patrón que los conectores de
Airtable/Dropbox).

## Flujo end-to-end (ya vigente, esta pieza cierra el último tramo)

```
Tarea Programada de Cowork (cada 1-2h)
  → intake-trigger        lee Airtable: ¿hay una entidad en "CCH To do"?
  → return-orchestrator   junta datos de Airtable + Dropbox (via source-resolver)
  → [skills de núcleo/módulo]  producen los writes lógicos (form/worksheet/line/value)
  → cch-axcess-client     traduce esos writes a XML Tax Transfer
        → cch-axcess-mcp  (ESTE COMPONENTE) autentica, arma el XML, POST a CCH, poll de estado
  → completion-report     mail: qué se completó / qué falta revisar
```

Solo `cch-axcess-client` invoca los tools de este MCP. Ninguna otra skill lo
llama directo.

## Restricción operativa (explícita del usuario)

Esto corre **exclusivamente dentro de Claude Desktop**, en la misma PC 24/7
donde ya corren los conectores de Airtable y Dropbox. No debe requerir que
el usuario abra una terminal en ningún momento de la operación normal:

- El **setup inicial** (crear el venv, instalar dependencias, cargar
  credenciales en `.env`) lo hace Claude Code una sola vez, ahora.
- Una vez registrado en `claude_desktop_config.json` (`mcpServers`), **Claude
  Desktop levanta y mata el proceso Python solo**, exactamente igual que un
  conector — el usuario nunca ve ni toca una terminal.
- El único paso manual e inevitable es el **consentimiento OAuth inicial**
  (abrir una URL, loguearse con MFA, copiar un `code` de la barra de
  direcciones) — es un requisito del protocolo OAuth de CCH, no de este
  diseño, y ocurre una vez cada ~4 semanas (vida del refresh token) salvo que
  el scheduled lo renueve antes (lo hace, en cada corrida).

## Arquitectura

```
cch-axcess-mcp/
  pyproject.toml
  src/cch_axcess_mcp/
    config.py       # carga .env (raíz del repo), valida variables requeridas
    auth.py         # OAuth 2.0: authorize URL, exchange code, refresh; TokenCache en disco
    xml_builder.py  # arma el Payload XML (Tax Transfer) + ConfigurationXml → base64/UTF-16
    client.py       # llamadas HTTP a la API real: find_returns, import_batch, batch_status
    server.py       # FastMCP (SDK oficial Python de MCP): expone los tools por stdio
  tests/
    smoke_test.py   # contra la API REAL, sin mocks — se corre a mano cuando haya credenciales
```

Elegido sobre dos alternativas: (a) implementar el protocolo MCP a mano en
vez de usar el SDK oficial — descartado, reinventa algo que el SDK ya
resuelve bien; (b) un script único monolítico — descartado, mezclaría
auth/XML/HTTP en un solo archivo, más difícil de probar cada pieza por
separado contra la API real.

## Tools del MCP (v1)

| Tool | Qué hace | Endpoint real |
|---|---|---|
| `cch_get_oauth_url` | Arma la URL de consentimiento OAuth (uso esporádico) | `GET /connect/authorize` |
| `cch_exchange_code` | Canjea el `code` del consentimiento inicial por tokens | `POST /connect/token` (`authorization_code`) |
| `cch_auth_status` | Renueva el token contra el refresh guardado — llamar en cada corrida del scheduled | `POST /connect/token` (`refresh_token`) |
| `cch_find_return` | Busca returns existentes por TaxYear (oblig.) + ClientID/ReturnType | `GET Returns` |
| `cch_import_batch` | Arma el XML Tax Transfer desde views/sections/fields ya resueltos y lo sube | `POST ReturnsImportBatch` |
| `cch_poll_batch` | Consulta estado de un batch de import/export | `GET BatchStatus` |

**Fuera de alcance de v1 — quedan como `NotImplementedError` explícito, no
se inventa el contrato hasta confirmarlo en el portal de desarrollador:**
`create_return_version`, `submit_export` + `stream_file`, `efile_status`.

## Manejo de errores

Las llamadas HTTP usan `raise_for_status()`: un 400/401/500 de CCH sube tal
cual a Claude (con el body de la respuesta, que trae el detalle del error),
en vez de tragarse el error o devolver un mensaje genérico. Esto importa
porque las pruebas son contra la API real — necesitamos ver el error real de
CCH para diagnosticar (ej. `RCRIU` = return in use).

## Testing — sin mocks, contra la API real

Por decisión explícita del usuario, no se testea con HTTP mockeado. En su
lugar, un script de smoke test (`tests/smoke_test.py`) ejercita la secuencia
real, de menor a mayor riesgo:

1. `cch_auth_status` — confirma que el refresh token vivo funciona.
2. `cch_find_return` (solo lectura) — confirma auth + subscription key +
   conectividad contra un cliente real (ej. SALVIN7).
3. `cch_import_batch` — **se prueba recién cuando existan los field codes
   reales del 1065** (Partnership); antes de eso, escribir sería alto riesgo
   sin un mapeo de campos confirmado. Hasta entonces, el smoke test se
   detiene después del paso 2.

## Pendientes conocidos (no bloquean el scaffold, sí el uso real)

- **Credenciales en `.env`**: `CCH_OIP_CLIENT_ID/SECRET`, `CCH_OIP_REDIRECT_URI`,
  `CCH_OIP_ACCOUNT_NUMBER`, `CCH_OIP_SUBSCRIPTION_KEY` (producto "Tax APIs"
  del portal, no "All APIs - Limited Use") — el usuario los completa a mano
  en `.env` (no se pasan por chat).
- **`CCH_OIP_INTEGRATOR_KEY`**: header que pide el "Try it" del portal; su
  origen no se resolvió (no salió en Profile ni en el registro de la app
  OAuth). El código lo soporta si se completa, pero funciona sin él mientras
  no se confirme que es obligatorio.
- **Nombre exacto del header de subscription key**: el código asume
  `Ocp-Apim-Subscription-Key` (convención Azure APIM) — a confirmar contra
  una llamada real.
- **Field codes del 1065 (Partnership)**: `xml_builder` es genérico (recibe
  `Location`/`FieldID` ya resueltos) — faltan los códigos reales, que salen
  de exportar un 1065 terminado (ver `tax-transfer-format.md`).

## Registro en Claude Desktop

```json
{
  "mcpServers": {
    "cch-axcess": {
      "command": "C:\\Users\\ian\\perchik-architecture-skills\\cch-axcess-mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "cch_axcess_mcp.server"],
      "cwd": "C:\\Users\\ian\\perchik-architecture-skills\\cch-axcess-mcp"
    }
  }
}
```
