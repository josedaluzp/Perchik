import base64
import json
import os
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import requests

from .config import DEFAULT_TIMEOUT, Config


def raise_with_body(resp: requests.Response) -> None:
    """Como resp.raise_for_status(), pero preserva el body de la respuesta en
    el mensaje de la excepción — sin él no se puede diagnosticar un error real
    de CCH (ej. invalid_grant en auth, RCRIU en el import). Nunca incluir los
    headers del request acá: ahí vive el bearer token y la subscription key.

    Vive en este módulo y lo importa client.py también, para que el formato
    del error sea uno solo y no derive entre los dos."""
    if not resp.ok:
        raise RuntimeError(
            f"CCH {resp.status_code} {resp.request.method} {resp.url}: {resp.text[:2000]}"
        )


class TokenCache:
    """Persiste los tokens en un archivo local (gitignored). El refresh_token
    rota en cada refresh — hay que guardar siempre el más nuevo, nunca el
    original."""

    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text())

    def write(self, data: dict) -> None:
        """Mergea sobre lo existente (un refresh sin refresh_token en la
        respuesta no debe destruir el que ya teníamos) y escribe atómico via
        un archivo temporal + os.replace, para no dejar JSON truncado si el
        proceso muere a mitad de escritura.

        El archivo queda 0600 (solo el dueño lee/escribe). En Windows chmod es
        casi un no-op — la protección real ahí es la ACL del perfil de usuario,
        no esto — pero no cuesta nada y sirve si algún día corre en POSIX."""
        merged = {**self.read(), **data}
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        tmp_path.write_text(json.dumps(merged, indent=2))
        os.chmod(tmp_path, 0o600)  # antes del replace: nunca hay una ventana con permisos abiertos
        os.replace(tmp_path, self.path)


def build_authorize_url(config: Config, state: str = "") -> str:
    params = {
        "response_type": "code",
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "scope": config.scopes,
    }
    if config.account_number:
        params["acr_values"] = json.dumps(
            {"AccountNumber": config.account_number}, separators=(",", ":")
        )
    if state:
        params["state"] = state
    return f"{config.auth_base}/authorize?{urlencode(params)}"


def _basic_auth_header(config: Config) -> str:
    raw = f"{config.client_id}:{config.client_secret}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def _post_token(config: Config, body: dict) -> dict:
    resp = requests.post(
        f"{config.auth_base}/token",
        headers={
            "Authorization": _basic_auth_header(config),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=body,
        timeout=DEFAULT_TIMEOUT,
    )
    raise_with_body(resp)
    tokens = resp.json()
    tokens["obtained_at"] = time.time()
    return tokens


def exchange_code(config: Config, cache: TokenCache, code: str) -> dict:
    """Uso único: canjea el authorization code del consentimiento inicial."""
    tokens = _post_token(
        config,
        {
            "code": code,
            "redirect_uri": config.redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    cache.write(tokens)
    return tokens


def _find_refresh_token(config: Config, cache: TokenCache) -> Optional[str]:
    """Fuente única de verdad para de dónde puede venir el refresh_token:
    primero el cache file, y si no está, el fallback CCH_OIP_REFRESH_TOKEN
    (donde .env.example dice que va el token post-consentimiento inicial)."""
    return cache.read().get("refresh_token") or os.environ.get("CCH_OIP_REFRESH_TOKEN")


def has_refresh_token(config: Config, cache: TokenCache) -> bool:
    """Chequea las mismas dos fuentes que refresh() acepta, para que el guard
    de los tests de integración no pueda divergir de la lógica real."""
    return bool(_find_refresh_token(config, cache))


def refresh(config: Config, cache: TokenCache) -> dict:
    """Renueva access+refresh token. Resetea la expiración de ambos (ver
    oauth-auth.md) — por eso conviene llamarlo en cada corrida del scheduled."""
    refresh_token = _find_refresh_token(config, cache)
    if not refresh_token:
        raise RuntimeError(
            "No hay refresh_token disponible. Corré cch_get_oauth_url + cch_exchange_code primero."
        )
    tokens = _post_token(
        config,
        {
            "refresh_token": refresh_token,
            "redirect_uri": config.redirect_uri,
            "grant_type": "refresh_token",
        },
    )
    cache.write(tokens)
    return tokens


def get_valid_access_token(config: Config, cache: TokenCache) -> str:
    current = cache.read()
    expires_in = current.get("expires_in", 0)
    obtained_at = current.get("obtained_at", 0)
    if current.get("access_token") and time.time() < obtained_at + expires_in - 60:
        return current["access_token"]
    tokens = refresh(config, cache)
    return tokens["access_token"]
