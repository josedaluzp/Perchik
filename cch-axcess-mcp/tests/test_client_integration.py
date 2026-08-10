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
