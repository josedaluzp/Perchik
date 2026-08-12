# cch-axcess-mcp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MCP (stdio) server that lets `cch-axcess-client` authenticate against CCH Axcess (OAuth 2.0) and read/write returns via Tax Services v2 (OIP), so it can run unattended inside Claude Desktop's scheduled flow.

**Architecture:** A Python package (`cch-axcess-mcp/`) with five focused modules — `config` (env loading), `auth` (OAuth + token cache), `xml_builder` (Tax Transfer XML), `client` (HTTP calls to CCH), `server` (FastMCP tool registration) — wired together in `server.py`, which Claude Desktop launches as a subprocess via `mcpServers` config.

**Tech Stack:** Python 3.12 (installed via winget this session), `mcp` (official Python MCP SDK, `FastMCP`), `requests`, `python-dotenv`, `pytest`.

## Global Constraints

- **No mocks.** Every test either exercises real local logic (config parsing, XML building, token-cache file I/O — no network involved, nothing to mock) or makes a real HTTP call against CCH's live API, skipped cleanly via `pytest.mark.skipif` when credentials aren't loaded yet. Never fake the CCH API.
- **No git commits during this implementation.** This repo is being worked locally for this feature; use the `session-log` skill at the end of the session instead of git history. Do not run `git add`/`git commit` as part of any task below.
- **Zero terminal for the end user.** Once `server.py` is registered in `claude_desktop_config.json`, Claude Desktop owns the process lifecycle. All setup/testing in this plan is run by the implementer (in a terminal), never by the Perchik team day-to-day.
- **Only `cch-axcess-client` invokes these tools.** No other skill should call this MCP directly.
- **v1 scope excludes** `create_return_version`, `submit_export`, `stream_file`, `efile_status` — their real endpoints aren't confirmed yet against the developer portal. They stay as explicit `NotImplementedError` in `client.py` (already written) — do not implement guesses for them in this plan.
- **Secrets never in code or chat** — only in `C:\Users\ian\perchik-architecture-skills\.env` (gitignored). Variable names are fixed by `.env.example`, already updated this session with `CCH_OIP_SUBSCRIPTION_KEY` and `CCH_OIP_INTEGRATOR_KEY`.
- Repo root: `C:\Users\ian\perchik-architecture-skills`. Package root: `C:\Users\ian\perchik-architecture-skills\cch-axcess-mcp`.

---

## Task 1: Project setup + config loader tests

**Files:**
- Modify: `cch-axcess-mcp/pyproject.toml` (add `dev` dependency group with `pytest`)
- Modify: `cch-axcess-mcp/src/cch_axcess_mcp/config.py` (already exists from earlier this session — no code change expected, this task adds its test)
- Create: `cch-axcess-mcp/tests/__init__.py`
- Create: `cch-axcess-mcp/tests/test_config.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: `cch_axcess_mcp.config.load_config() -> Config`, `cch_axcess_mcp.config.REQUIRED_VARS: list[str]`, `Config` dataclass fields (`client_id`, `client_secret`, `redirect_uri`, `subscription_key`, `account_number`, `integrator_key`, `scopes`, `auth_base`, `api_base`, `token_cache_path`) — every later task imports `Config`/`load_config` from here.

- [ ] **Step 1: Add the `dev` dependency group to `pyproject.toml`**

Edit `cch-axcess-mcp/pyproject.toml`, add after the `dependencies` list:

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0"]
```

- [ ] **Step 2: Create the venv and install the package with dev dependencies**

Run (from `cch-axcess-mcp/`):
```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
```
Expected: installs `mcp`, `requests`, `python-dotenv`, `pytest` with no errors.

- [ ] **Step 3: Write the failing test**

Create `cch-axcess-mcp/tests/__init__.py` (empty file).

Create `cch-axcess-mcp/tests/test_config.py`:
```python
import pytest

from cch_axcess_mcp.config import REQUIRED_VARS, load_config


def test_load_config_raises_when_required_vars_missing(monkeypatch):
    for name in REQUIRED_VARS:
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError, match="Faltan variables de entorno"):
        load_config()


def test_load_config_reads_required_and_default_values(monkeypatch):
    monkeypatch.setenv("CCH_OIP_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("CCH_OIP_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("CCH_OIP_REDIRECT_URI", "https://perchikcpa.com/cch-oauth-callback")
    monkeypatch.setenv("CCH_OIP_SUBSCRIPTION_KEY", "test-subscription-key")
    monkeypatch.delenv("CCH_OIP_ACCOUNT_NUMBER", raising=False)
    monkeypatch.delenv("CCH_OIP_INTEGRATOR_KEY", raising=False)

    config = load_config()

    assert config.client_id == "test-client-id"
    assert config.client_secret == "test-secret"
    assert config.redirect_uri == "https://perchikcpa.com/cch-oauth-callback"
    assert config.subscription_key == "test-subscription-key"
    assert config.account_number is None
    assert config.integrator_key is None
    assert config.api_base == "https://api.cchaxcess.com"
    assert "offline_access" in config.scopes
```

- [ ] **Step 4: Run the tests to verify they pass** (implementation already exists from earlier this session, so this confirms it rather than failing first — that's expected here, not a TDD violation, since `config.py` predates this plan)

Run: `.venv/Scripts/python.exe -m pytest tests/test_config.py -v`
Expected: both tests PASS. If `test_load_config_reads_required_and_default_values` fails on the `scopes` default, check that `config.py`'s default matches `CCHAxcess_data_writeaccess offline_access openid IDInfo` exactly.

---

## Task 2: XML builder tests

**Files:**
- Modify: `cch-axcess-mcp/src/cch_axcess_mcp/xml_builder.py` (already exists — no code change expected)
- Create: `cch-axcess-mcp/tests/test_xml_builder.py`

**Interfaces:**
- Consumes: nothing (pure functions, no dependency on Task 1).
- Produces: `cch_axcess_mcp.xml_builder.build_payload_xml_bytes(return_header: dict, taxpayer_details: dict, views: list) -> bytes`, `build_configuration_xml(...) -> str`, `build_and_encode(return_header, taxpayer_details, views) -> str` — Task 6 (server tools) calls `build_and_encode` and `build_configuration_xml` directly.

- [ ] **Step 1: Write the failing test**

Create `cch-axcess-mcp/tests/test_xml_builder.py`:
```python
import base64
from xml.etree import ElementTree as ET

from cch_axcess_mcp.xml_builder import (
    build_and_encode,
    build_configuration_xml,
    build_payload_xml_bytes,
)

RETURN_HEADER = {
    "ClientID": "SALVIN7",
    "TaxYear": "2025",
    "ReturnType": "P",
    "ReturnGroupName": "Default",
    "Country": "US",
    "OfficeName": "Dallas",
    "BusinessUnitName": "Development",
    "ConfigurationSet": "Default",
    "ReturnVersion": "1",
    "EINorSSN": "12-3456789",
    "ControlNumber": "20260810000001",
}
TAXPAYER_DETAILS = {"NameLine1": "SALVIN7", "NameLine2": "LLC"}
VIEWS = [
    {
        "hierarchy": "Federal\\Partner Information",
        "entity_id": 1,
        "sections": [
            {"name": "General", "fields": [{"location": "IPDSPTR.1", "value": "50.0000"}]}
        ],
    }
]


def test_build_payload_xml_bytes_is_valid_and_has_expected_structure():
    xml_bytes = build_payload_xml_bytes(RETURN_HEADER, TAXPAYER_DETAILS, VIEWS)

    root = ET.fromstring(xml_bytes)
    assert root.tag == "Payload"
    assert root.attrib["DataType"] == "Tax"
    assert root.attrib["DataFormat"] == "Standard"

    return_header = root.find("TaxReturn/ReturnHeader")
    assert return_header.attrib["ClientID"] == "SALVIN7"
    assert return_header.attrib["ReturnType"] == "P"

    taxpayer = root.find("TaxReturn/TaxPayerDetails")
    assert taxpayer.attrib["NameLine1"] == "SALVIN7"

    identifier = root.find("TaxReturn/View/Identifier")
    assert identifier.attrib["Hierarchy"] == "Federal\\Partner Information"

    entity = root.find("TaxReturn/View/Controls/Entity")
    assert entity.attrib["ID"] == "1"

    field = root.find("TaxReturn/View/WorkSheetSection/FieldData")
    assert field.attrib["Location"] == "IPDSPTR.1"
    assert field.attrib["LocationType"] == "FieldID"
    assert field.attrib["Value"] == "50.0000"


def test_build_payload_xml_bytes_omits_controls_when_no_entity_id():
    views = [{"hierarchy": "Federal\\General\\Basic Data", "sections": []}]
    xml_bytes = build_payload_xml_bytes(RETURN_HEADER, TAXPAYER_DETAILS, views)

    root = ET.fromstring(xml_bytes)
    assert root.find("TaxReturn/View/Controls") is None


def test_build_and_encode_roundtrips_through_base64():
    encoded = build_and_encode(RETURN_HEADER, TAXPAYER_DETAILS, VIEWS)
    decoded_bytes = base64.b64decode(encoded)

    assert decoded_bytes == build_payload_xml_bytes(RETURN_HEADER, TAXPAYER_DETAILS, VIEWS)


def test_build_configuration_xml_default_options():
    xml_str = build_configuration_xml()
    root = ET.fromstring(xml_str)

    assert root.tag == "TaxDataImportOptions"
    assert root.find("ImportMode").text == "MatchAndUpdate"
    assert root.find("CaseSensitiveMatching").text == "false"
    assert root.find("InvalidContentErrorHandling").text == "RejectReturnOnAnyError"
    assert root.find("CalcReturnAfterImport").text == "false"


def test_build_configuration_xml_custom_options():
    xml_str = build_configuration_xml(import_mode="Overwrite", calc_return_after_import=True)
    root = ET.fromstring(xml_str)

    assert root.find("ImportMode").text == "Overwrite"
    assert root.find("CalcReturnAfterImport").text == "true"
```

- [ ] **Step 2: Run the tests**

Run: `.venv/Scripts/python.exe -m pytest tests/test_xml_builder.py -v`
Expected: all 5 PASS. If `test_build_payload_xml_bytes_omits_controls_when_no_entity_id` fails, check `xml_builder.py`'s `if view.get("entity_id") is not None:` guard.

---

## Task 3: Auth — token cache + authorize URL tests

**Files:**
- Modify: `cch-axcess-mcp/src/cch_axcess_mcp/auth.py` (already exists — no code change expected)
- Create: `cch-axcess-mcp/tests/test_auth.py`

**Interfaces:**
- Consumes: `Config` dataclass from Task 1 (`cch_axcess_mcp.config.Config`).
- Produces: `cch_axcess_mcp.auth.TokenCache(path).read() -> dict`, `.write(data: dict) -> None`; `build_authorize_url(config: Config, state: str = "") -> str` — Task 6's `cch_get_oauth_url` tool calls this directly.

- [ ] **Step 1: Write the failing test**

Create `cch-axcess-mcp/tests/test_auth.py`:
```python
from pathlib import Path

from cch_axcess_mcp.auth import TokenCache, build_authorize_url
from cch_axcess_mcp.config import Config


def _make_config(**overrides):
    defaults = dict(
        client_id="test-client-id",
        client_secret="test-secret",
        redirect_uri="https://perchikcpa.com/cch-oauth-callback",
        subscription_key="test-subscription-key",
        account_number="168142",
        integrator_key=None,
        scopes="CCHAxcess_data_writeaccess offline_access openid IDInfo",
        auth_base="https://login.cchaxcess.com/ps/auth/v1.0/core/connect",
        api_base="https://api.cchaxcess.com",
        token_cache_path=Path("unused.json"),
    )
    defaults.update(overrides)
    return Config(**defaults)


def test_token_cache_read_returns_empty_dict_when_missing(tmp_path):
    cache = TokenCache(tmp_path / "missing.json")
    assert cache.read() == {}


def test_token_cache_write_then_read_roundtrips(tmp_path):
    cache = TokenCache(tmp_path / "tokens.json")
    cache.write({"access_token": "abc", "refresh_token": "def", "expires_in": 600})

    assert cache.read() == {"access_token": "abc", "refresh_token": "def", "expires_in": 600}


def test_build_authorize_url_includes_required_params():
    config = _make_config()
    url = build_authorize_url(config, state="xyz")

    assert url.startswith("https://login.cchaxcess.com/ps/auth/v1.0/core/connect/authorize?")
    assert "client_id=test-client-id" in url
    assert "response_type=code" in url
    assert "redirect_uri=https%3A%2F%2Fperchikcpa.com%2Fcch-oauth-callback" in url
    assert "acr_values=%7B%22AccountNumber%22%3A%22168142%22%7D" in url
    assert "state=xyz" in url


def test_build_authorize_url_omits_acr_values_without_account_number():
    config = _make_config(account_number=None)
    url = build_authorize_url(config)
    assert "acr_values" not in url
```

- [ ] **Step 2: Run the tests**

Run: `.venv/Scripts/python.exe -m pytest tests/test_auth.py -v`
Expected: all 5 PASS.

---

## Task 4: HTTP client — pure helper test + real integration tests (skip-guarded)

**Files:**
- Modify: `cch-axcess-mcp/src/cch_axcess_mcp/client.py` (already exists — no code change expected)
- Create: `cch-axcess-mcp/tests/test_client.py`
- Create: `cch-axcess-mcp/tests/test_client_integration.py`

**Interfaces:**
- Consumes: `Config`/`load_config` (Task 1), `TokenCache` (Task 3).
- Produces: `cch_axcess_mcp.client.find_returns(config, cache, tax_year, client_id=None, return_type=None) -> dict`, `import_batch(config, cache, file_data_list_b64: list, configuration_xml: str) -> dict`, `batch_status(config, cache, batch_guid, expand_items=False) -> dict` — Task 6's tools call these directly.

- [ ] **Step 1: Write the failing test for the pure helper**

Create `cch-axcess-mcp/tests/test_client.py`:
```python
from cch_axcess_mcp.client import _escape_odata


def test_escape_odata_doubles_single_quotes():
    assert _escape_odata("O'Brien") == "O''Brien"


def test_escape_odata_leaves_plain_strings_unchanged():
    assert _escape_odata("SALVIN7") == "SALVIN7"
```

- [ ] **Step 2: Run it**

Run: `.venv/Scripts/python.exe -m pytest tests/test_client.py -v`
Expected: both PASS.

- [ ] **Step 3: Write the real-API integration tests (skip cleanly without credentials)**

Create `cch-axcess-mcp/tests/test_client_integration.py`:
```python
import pytest

from cch_axcess_mcp.auth import TokenCache
from cch_axcess_mcp.client import batch_status, find_returns
from cch_axcess_mcp.config import load_config

try:
    _config = load_config()
    _cache = TokenCache(_config.token_cache_path)
    _has_refresh_token = bool(_cache.read().get("refresh_token"))
except RuntimeError:
    _has_refresh_token = False

pytestmark = pytest.mark.skipif(
    not _has_refresh_token,
    reason="Sin refresh_token en el cache todavía — corré el consentimiento OAuth inicial (Task 5) primero.",
)


def test_find_returns_requires_tax_year_and_returns_json_shape():
    config = load_config()
    cache = TokenCache(config.token_cache_path)

    result = find_returns(config, cache, tax_year="2025")

    assert "Returns" in result
    assert "TotalCount" in result


def test_batch_status_with_unknown_guid_does_not_crash():
    config = load_config()
    cache = TokenCache(config.token_cache_path)

    result = batch_status(config, cache, batch_guid="00000000-0000-0000-0000-000000000000")

    assert isinstance(result, dict)
```

- [ ] **Step 4: Run it now (expected to SKIP until Task 5 is done)**

Run: `.venv/Scripts/python.exe -m pytest tests/test_client_integration.py -v`
Expected: both tests **SKIPPED** with the reason message above (no `refresh_token` yet). This is correct at this point in the plan — do not treat as failure.

---

## Task 5: OAuth initial consent (real, human-in-the-loop) — populate the token cache

**Files:**
- None created/modified — this task exercises `auth.py` for real to produce `cch-axcess-mcp/.token_cache.json` (gitignored, created at runtime).

**Interfaces:**
- Consumes: `build_authorize_url`, `exchange_code`, `TokenCache` (Task 3), `load_config` (Task 1).
- Produces: a populated `.token_cache.json` with a live `refresh_token` — required for Task 4's integration tests to stop skipping, and for Task 6/7's live checks.

**Prerequisite:** the user has filled `CCH_OIP_CLIENT_ID`, `CCH_OIP_CLIENT_SECRET`, `CCH_OIP_REDIRECT_URI`, `CCH_OIP_ACCOUNT_NUMBER`, `CCH_OIP_SUBSCRIPTION_KEY` in `C:\Users\ian\perchik-architecture-skills\.env`. If any are still blank, stop here and ask the user to fill them before continuing.

- [ ] **Step 1: Get the authorize URL**

Run (from `cch-axcess-mcp/`):
```bash
.venv/Scripts/python.exe -c "from cch_axcess_mcp.config import load_config; from cch_axcess_mcp.auth import build_authorize_url; print(build_authorize_url(load_config()))"
```
Expected: prints a `https://login.cchaxcess.com/...` URL. If it raises `RuntimeError: Faltan variables de entorno`, go fill those in `.env` first.

- [ ] **Step 2: Open the URL in a browser, approve the app**

Log in with the firm's account number + credentials/MFA, approve "Perchik-1065-Automation". CCH redirects to `CCH_OIP_REDIRECT_URI?code=...` — the page may 404, that's fine. Copy the `code` value from the address bar (URL-decode it if it contains `%` sequences).

- [ ] **Step 3: Exchange the code for tokens**

Run:
```bash
.venv/Scripts/python.exe -c "from cch_axcess_mcp.config import load_config; from cch_axcess_mcp.auth import TokenCache, exchange_code; c = load_config(); exchange_code(c, TokenCache(c.token_cache_path), 'PASTE_CODE_HERE')"
```
Expected: no exception. Confirm `cch-axcess-mcp/.token_cache.json` now exists and contains `access_token`, `refresh_token`, `expires_in`.

- [ ] **Step 4: Verify refresh works**

Run:
```bash
.venv/Scripts/python.exe -c "from cch_axcess_mcp.config import load_config; from cch_axcess_mcp.auth import TokenCache, refresh; c = load_config(); print(refresh(c, TokenCache(c.token_cache_path))['expires_in'])"
```
Expected: prints a number (seconds), no exception. `.token_cache.json` should now have a **new** `refresh_token` value (CCH rotates it on every refresh).

- [ ] **Step 5: Re-run Task 4's integration tests — they should run for real now**

Run: `.venv/Scripts/python.exe -m pytest tests/test_client_integration.py -v`
Expected: both tests **PASS** for real against CCH. If `test_find_returns_requires_tax_year_and_returns_json_shape` fails with a 400, check the error body in the exception message — it likely means the `$filter` syntax needs adjusting (compare against `tax-transfer-format.md`'s verified example).

---

## Task 6: MCP server — wire the tools

**Files:**
- Create: `cch-axcess-mcp/src/cch_axcess_mcp/server.py`

**Interfaces:**
- Consumes: everything from Tasks 1-4 (`load_config`, `TokenCache`, `build_authorize_url`, `exchange_code`, `refresh`, `find_returns`, `import_batch`, `batch_status`, `build_and_encode`, `build_configuration_xml`).
- Produces: `mcp` (the `FastMCP` instance) importable as `cch_axcess_mcp.server.mcp`; `main()` entry point registered in `pyproject.toml` as `cch-axcess-mcp`. Task 7 registers this as the Desktop-launched process.

- [ ] **Step 1: Write `server.py`**

```python
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .auth import TokenCache, build_authorize_url, exchange_code, refresh
from .client import batch_status, find_returns, import_batch
from .config import load_config
from .xml_builder import build_and_encode, build_configuration_xml

mcp = FastMCP("cch-axcess")
_config = load_config()
_cache = TokenCache(_config.token_cache_path)


@mcp.tool()
def cch_get_oauth_url(state: str = "") -> str:
    """Genera la URL de consentimiento OAuth (uso único/esporádico). Abrila en un
    browser, logueate con el account number del firm, aprobá la app, y pasá el
    'code' que queda en la barra de direcciones a cch_exchange_code."""
    return build_authorize_url(_config, state=state)


@mcp.tool()
def cch_exchange_code(code: str) -> dict:
    """Canjea el authorization code por access/refresh token y los guarda en
    el cache local. Uso único, solo para el consentimiento inicial."""
    tokens = exchange_code(_config, _cache, code)
    return {"authenticated": True, "expires_in": tokens.get("expires_in")}


@mcp.tool()
def cch_auth_status() -> dict:
    """Renueva el token contra el refresh_token guardado. Llamar en cada
    corrida del scheduled (aunque no haya entidades para procesar) para que
    el refresh token nunca expire por inactividad."""
    tokens = refresh(_config, _cache)
    return {"authenticated": True, "expires_in": tokens.get("expires_in")}


@mcp.tool()
def cch_find_return(
    tax_year: str, client_id: Optional[str] = None, return_type: Optional[str] = None
) -> dict:
    """Busca returns existentes en CCH. return_type 'P' = 1065 Partnership,
    'I' = Individual, 'C' = 1120 Corporation."""
    return find_returns(_config, _cache, tax_year, client_id=client_id, return_type=return_type)


@mcp.tool()
def cch_import_batch(
    return_header: dict,
    taxpayer_details: dict,
    views: list,
    import_mode: str = "MatchAndUpdate",
    calc_after_import: bool = False,
) -> dict:
    """Arma el XML Tax Transfer a partir de views/sections/fields ya resueltos
    (con los Location/FieldID reales del 1065) y lo sube via ReturnsImportBatch.
    Devuelve {ExecutionID, FileResults[]} — pollear ExecutionID con cch_poll_batch."""
    file_b64 = build_and_encode(return_header, taxpayer_details, views)
    config_xml = build_configuration_xml(
        import_mode=import_mode, calc_return_after_import=calc_after_import
    )
    return import_batch(_config, _cache, [file_b64], config_xml)


@mcp.tool()
def cch_poll_batch(batch_guid: str, expand_items: bool = False) -> dict:
    """Consulta el estado de un batch de import/export (ExecutionID de
    cch_import_batch). Pollear cada 1-2 min."""
    return batch_status(_config, _cache, batch_guid, expand_items=expand_items)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the module wires up without starting the blocking server loop**

Run (from `cch-axcess-mcp/`):
```bash
.venv/Scripts/python.exe -c "from cch_axcess_mcp.server import mcp; print(mcp.name)"
```
Expected: prints `cch-axcess`, no exception. If it raises `RuntimeError: Faltan variables de entorno`, `.env` is still missing a required value (see Task 5's prerequisite).

- [ ] **Step 3: Verify each tool is registered**

Run:
```bash
.venv/Scripts/python.exe -c "
import asyncio
from cch_axcess_mcp.server import mcp
tools = asyncio.run(mcp.list_tools())
print(sorted(t.name for t in tools))
"
```
Expected: `['cch_auth_status', 'cch_exchange_code', 'cch_find_return', 'cch_get_oauth_url', 'cch_import_batch', 'cch_poll_batch']`.

---

## Task 7: Register in Claude Desktop

**Files:**
- Modify: `%APPDATA%\Claude\claude_desktop_config.json` (Windows path — outside the repo)

**Interfaces:**
- Consumes: `main()` entry point from Task 6, the venv's `python.exe` path.
- Produces: nothing further downstream — this is the last task.

- [ ] **Step 1: Locate (or create) the Desktop config file**

Run:
```bash
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```
(PowerShell) or open it directly in File Explorer at `%APPDATA%\Claude\claude_desktop_config.json`. If it doesn't exist, create it with `{}` as the starting content.

- [ ] **Step 2: Add the `cch-axcess` entry**

Merge this into the existing JSON's `mcpServers` object (create `mcpServers` if it doesn't exist yet — don't overwrite other servers already configured, like Airtable/Dropbox connectors if they happen to live in this same file):
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

- [ ] **Step 3: Restart Claude Desktop and verify**

Close Claude Desktop completely (check it's not still running in the system tray) and reopen it. Start a new chat and ask: *"¿Tenés disponible el tool cch_auth_status?"* — Claude should confirm it sees the `cch-axcess` MCP server and its tools. Then actually call it (e.g. *"llamá a cch_auth_status"*) and confirm it returns `{"authenticated": true, "expires_in": ...}` instead of an error.

- [ ] **Step 4: Confirm only `cch-axcess-client`'s SKILL.md references these tools**

Open `.claude/skills/cch-axcess-client/SKILL.md` and confirm/add a short note under "Cómo lo implementa" pointing to `cch-axcess-mcp` and listing the six tool names from Task 6, so future readers know where the implementation lives. Do not add tool references to any other skill.
