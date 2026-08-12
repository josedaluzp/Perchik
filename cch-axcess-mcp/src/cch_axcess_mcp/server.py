from typing import Optional

import anyio.to_thread
from mcp.server.fastmcp import FastMCP

from .auth import TokenCache, build_authorize_url, exchange_code, refresh
from .client import batch_status, find_returns, import_batch
from .config import load_config
from .xml_builder import build_and_encode, build_configuration_xml

mcp = FastMCP("cch-axcess")

_config = None
_cache = None


def _get_config():
    """Carga la config de forma perezosa (recién cuando se invoca una tool),
    no al importar el módulo — así una variable de entorno faltante se
    reporta como un error de tool call legible en vez de tirar abajo el
    proceso entero antes de que Desktop pueda mostrar nada (el operador
    'nunca ve ni toca una terminal')."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def _get_cache():
    global _cache
    if _cache is None:
        _cache = TokenCache(_get_config().token_cache_path)
    return _cache


@mcp.tool()
async def cch_get_oauth_url(state: str = "") -> str:
    """Genera la URL de consentimiento OAuth (uso único/esporádico). Abrila en un
    browser, logueate con el account number del firm, aprobá la app, y pasá el
    'code' que queda en la barra de direcciones a cch_exchange_code."""
    return build_authorize_url(_get_config(), state=state)


@mcp.tool()
async def cch_exchange_code(code: str) -> dict:
    """Canjea el authorization code por access/refresh token y los guarda en
    el cache local. Uso único, solo para el consentimiento inicial."""
    tokens = await anyio.to_thread.run_sync(exchange_code, _get_config(), _get_cache(), code)
    return {"authenticated": True, "expires_in": tokens.get("expires_in")}


@mcp.tool()
async def cch_auth_status() -> dict:
    """Renueva el token contra el refresh_token guardado. Llamar en cada
    corrida del scheduled (aunque no haya entidades para procesar) para que
    el refresh token nunca expire por inactividad."""
    tokens = await anyio.to_thread.run_sync(refresh, _get_config(), _get_cache())
    return {"authenticated": True, "expires_in": tokens.get("expires_in")}


@mcp.tool()
async def cch_find_return(
    tax_year: str, client_id: Optional[str] = None, return_type: Optional[str] = None
) -> dict:
    """Busca returns existentes en CCH. return_type 'P' = 1065 Partnership,
    'I' = Individual, 'C' = 1120 Corporation."""
    return await anyio.to_thread.run_sync(
        lambda: find_returns(
            _get_config(), _get_cache(), tax_year, client_id=client_id, return_type=return_type
        )
    )


@mcp.tool()
async def cch_import_batch(
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
    return await anyio.to_thread.run_sync(
        import_batch, _get_config(), _get_cache(), [file_b64], config_xml
    )


@mcp.tool()
async def cch_poll_batch(batch_guid: str, expand_items: bool = False) -> dict:
    """Consulta el estado de un batch de import/export (ExecutionID de
    cch_import_batch). Pollear cada 1-2 min."""
    return await anyio.to_thread.run_sync(
        lambda: batch_status(_get_config(), _get_cache(), batch_guid, expand_items=expand_items)
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
