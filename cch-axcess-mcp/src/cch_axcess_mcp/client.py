from typing import Optional

import requests

from .auth import TokenCache, get_valid_access_token
from .config import TAX_SERVICES_PATH, Config


def _headers(config: Config, cache: TokenCache) -> dict:
    token = get_valid_access_token(config, cache)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        # TODO: confirmar el nombre exacto de este header contra una llamada real.
        # Asumimos la convención Azure APIM (Ocp-Apim-Subscription-Key).
        "Ocp-Apim-Subscription-Key": config.subscription_key,
    }
    if config.integrator_key:
        # TODO: IntegratorKey todavía sin resolver de dónde sale (no salió ni
        # en Profile del dev portal ni en el registro de la app OAuth).
        headers["IntegratorKey"] = config.integrator_key
    return headers


def _base_url(config: Config) -> str:
    return f"{config.api_base}{TAX_SERVICES_PATH}"


def _escape_odata(value: str) -> str:
    return value.replace("'", "''")


def _raise_with_body(resp: requests.Response) -> None:
    """Como resp.raise_for_status(), pero preserva el body de la respuesta en
    el mensaje de la excepción — el spec pide poder ver el error real de CCH
    (ej. RCRIU) para diagnosticar. Nunca incluir los headers del request acá:
    ahí vive el bearer token y la subscription key."""
    if not resp.ok:
        raise RuntimeError(
            f"CCH {resp.status_code} {resp.request.method} {resp.url}: {resp.text[:2000]}"
        )


def find_returns(
    config: Config,
    cache: TokenCache,
    tax_year: str,
    client_id: Optional[str] = None,
    return_type: Optional[str] = None,
) -> dict:
    """GET Returns. TaxYear es obligatorio en el $filter (sin él, CCH devuelve 400)."""
    filters = [f"TaxYear eq '{_escape_odata(tax_year)}'"]
    if client_id:
        filters.append(f"ClientID eq '{_escape_odata(client_id)}'")
    if return_type:
        filters.append(f"ReturnType eq '{_escape_odata(return_type)}'")
    resp = requests.get(
        f"{_base_url(config)}/Returns",
        headers=_headers(config, cache),
        params={"$filter": " and ".join(filters)},
        timeout=30,
    )
    _raise_with_body(resp)
    return resp.json()


def import_batch(
    config: Config, cache: TokenCache, file_data_list_b64: list, configuration_xml: str
) -> dict:
    """POST ReturnsImportBatch. Devuelve {ExecutionID, FileResults[]}."""
    body = {"FileDataList": file_data_list_b64, "ConfigurationXml": configuration_xml}
    resp = requests.post(
        f"{_base_url(config)}/ReturnsImportBatch",
        headers=_headers(config, cache),
        json=body,
        timeout=60,
    )
    _raise_with_body(resp)
    return resp.json()


def batch_status(
    config: Config, cache: TokenCache, batch_guid: str, expand_items: bool = False
) -> dict:
    """GET BatchStatus. Pollear cada 1-2 min para import/export, 5-10 min para print/e-file."""
    filter_expr = f"BatchGuid eq '{_escape_odata(batch_guid)}'"
    if expand_items:
        filter_expr += " and Expand eq 'Items'"
    resp = requests.get(
        f"{_base_url(config)}/BatchStatus",
        headers=_headers(config, cache),
        params={"$filter": filter_expr},
        timeout=30,
    )
    _raise_with_body(resp)
    return resp.json()


# --- Pendientes: path/body exactos sin confirmar todavía contra el portal ---
# No se adivinan URLs acá — mejor fallar explícito que asumir mal un contrato.


def create_return_version(config: Config, cache: TokenCache, **kwargs) -> dict:
    raise NotImplementedError(
        "Falta confirmar path/body de 'Create a new version of the provided return' en el portal."
    )


def submit_export(config: Config, cache: TokenCache, **kwargs) -> dict:
    raise NotImplementedError(
        "Falta confirmar path/body de 'Submit a list of returns for export' en el portal."
    )


def stream_file(config: Config, cache: TokenCache, **kwargs) -> bytes:
    raise NotImplementedError(
        "Falta confirmar path/body de 'Stream the requested file' en el portal."
    )


def efile_status(config: Config, cache: TokenCache, **kwargs) -> dict:
    raise NotImplementedError(
        "Falta confirmar path/body de 'Retrieve the status of the e-filed returns' en el portal."
    )
