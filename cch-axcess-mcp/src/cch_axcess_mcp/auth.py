import base64
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

from .config import Config


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
        self.path.write_text(json.dumps(data, indent=2))


def build_authorize_url(config: Config, state: str = "") -> str:
    params = {
        "response_type": "code",
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "scope": config.scopes,
    }
    if config.account_number:
        params["acr_values"] = f'{{"AccountNumber":"{config.account_number}"}}'
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
        timeout=30,
    )
    resp.raise_for_status()
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


def refresh(config: Config, cache: TokenCache) -> dict:
    """Renueva access+refresh token. Resetea la expiración de ambos (ver
    oauth-auth.md) — por eso conviene llamarlo en cada corrida del scheduled."""
    current = cache.read()
    refresh_token = current.get("refresh_token") or os.environ.get("CCH_OIP_REFRESH_TOKEN")
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
