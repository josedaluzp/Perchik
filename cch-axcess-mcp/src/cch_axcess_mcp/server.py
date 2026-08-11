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
