# cch-axcess-mcp

Servidor MCP (stdio) que implementa el contrato de `cch-axcess-client` (ver
`../.claude/skills/cch-axcess-client/SKILL.md`): el único componente que habla
con la API real de CCH Axcess (Tax Services v2 / OIP). Las skills declaran
valores lógicos (`write`/`read`); este servidor los traduce a XML Tax
Transfer y llama a la API.

## Qué está implementado (real) vs pendiente

**Real, contra los endpoints ya confirmados en el portal de desarrollador:**
- OAuth 2.0 completo: `cch_get_oauth_url`, `cch_exchange_code`, `cch_auth_status` (refresh).
- `cch_find_return` → `GET Returns`
- `cch_import_batch` → `POST ReturnsImportBatch` (armado del XML Tax Transfer + base64/UTF-16)
- `cch_poll_batch` → `GET BatchStatus`

**Pendiente — paths/body no confirmados aún contra el portal, quedan como
`NotImplementedError` en `client.py` para no inventar un contrato:**
- Create a new version of the provided return
- Submit a list of returns for export / Stream the requested file
- Retrieve the status of the e-filed returns

**Sin resolver todavía (no bloquea lo de arriba, pero falta antes de un run real):**
- El header `IntegratorKey` que pide el "Try it" del portal — no salió ni en
  Profile (esa es la subscription key) ni en el registro de la app OAuth. El
  código ya soporta mandarlo (`CCH_OIP_INTEGRATOR_KEY`) apenas se consiga.
- El nombre exacto del header de subscription key — el código asume
  `Ocp-Apim-Subscription-Key` (convención Azure APIM); confirmar contra una
  llamada real y corregir en `client.py` si hace falta.
- Los **field codes del 1065** (Partnership) — `xml_builder` es genérico
  (toma `Location`/`FieldID` ya resueltos); quien llame a `cch_import_batch`
  necesita pasar los códigos reales, que salen de exportar un 1065 terminado
  (ver `tax-transfer-format.md`).

## Setup

```bash
cd cch-axcess-mcp
python -m venv .venv
.venv/Scripts/activate   # PowerShell: .venv\Scripts\Activate.ps1
pip install -e .
```

Completar los valores reales en el `.env` de la **raíz del repo** (nunca en
este folder, nunca committeados) — ver `.env.example` en la raíz. Variables
nuevas que agregamos ahí: `CCH_OIP_SUBSCRIPTION_KEY` (la del producto "Tax
APIs" del portal, **no** la de "All APIs - Limited Use") y
`CCH_OIP_INTEGRATOR_KEY` (opcional por ahora, hasta resolver de dónde sale).

## Consentimiento OAuth inicial (una sola vez / esporádico)

1. Con el paquete instalado, llamá `cch_get_oauth_url` (desde el servidor MCP
   o directo en un REPL de Python) → abrí esa URL en un browser, logueate con
   el account number del firm, aprobá la app.
2. CCH redirige a `CCH_OIP_REDIRECT_URI?code=...` — copiá el `code` de la
   barra de direcciones (la página puede tirar 404, no importa).
3. Llamá `cch_exchange_code(code)` → guarda `access_token`/`refresh_token` en
   `.token_cache.json` (gitignored, en esta misma carpeta). De ahí en más,
   `cch_auth_status` lo renueva solo — el scheduled debería llamarlo en cada
   corrida para que el refresh token nunca expire por inactividad.

## Registrar en Claude Desktop

En el config de Claude Desktop (`claude_desktop_config.json`), agregar en
`mcpServers`:

```json
{
  "mcpServers": {
    "cch-axcess": {
      "command": "C:\\ruta\\a\\cch-axcess-mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "cch_axcess_mcp.server"],
      "cwd": "C:\\ruta\\a\\cch-axcess-mcp"
    }
  }
}
```

Solo la skill `cch-axcess-client` debería invocar estos tools — las otras 24
skills de la suite declaran valores lógicos, no llaman a este MCP directo.
