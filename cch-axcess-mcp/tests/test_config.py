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
