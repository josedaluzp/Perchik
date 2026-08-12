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
