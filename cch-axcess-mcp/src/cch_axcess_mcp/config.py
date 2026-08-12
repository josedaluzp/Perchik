import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # cch-axcess-mcp/
_REPO_ROOT = _PACKAGE_ROOT.parent  # perchik-architecture-skills/

load_dotenv(_REPO_ROOT / ".env")
load_dotenv(_PACKAGE_ROOT / ".env")  # override local, si existe

TAX_SERVICES_PATH = "/taxservices/oiptax/api/v1"

# Timeouts de red, en un solo lugar. El import es más lento que el resto
# (CCH arma el batch del lado suyo antes de responder), por eso va aparte.
DEFAULT_TIMEOUT = 30
IMPORT_TIMEOUT = 60

REQUIRED_VARS = [
    "CCH_OIP_CLIENT_ID",
    "CCH_OIP_CLIENT_SECRET",
    "CCH_OIP_REDIRECT_URI",
    "CCH_OIP_SUBSCRIPTION_KEY",
]


@dataclass(frozen=True)
class Config:
    client_id: str
    client_secret: str
    redirect_uri: str
    subscription_key: str
    account_number: Optional[str]
    integrator_key: Optional[str]
    scopes: str
    auth_base: str
    api_base: str
    token_cache_path: Path


def load_config() -> Config:
    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            f"Faltan variables de entorno: {', '.join(missing)} (ver .env.example en la raíz del repo)"
        )

    return Config(
        client_id=os.environ["CCH_OIP_CLIENT_ID"],
        client_secret=os.environ["CCH_OIP_CLIENT_SECRET"],
        redirect_uri=os.environ["CCH_OIP_REDIRECT_URI"],
        subscription_key=os.environ["CCH_OIP_SUBSCRIPTION_KEY"],
        account_number=os.environ.get("CCH_OIP_ACCOUNT_NUMBER") or None,
        integrator_key=os.environ.get("CCH_OIP_INTEGRATOR_KEY") or None,
        scopes=os.environ.get(
            "CCH_OIP_SCOPES", "CCHAxcess_data_writeaccess offline_access openid IDInfo"
        ),
        auth_base=os.environ.get(
            "CCH_OIP_AUTH_BASE", "https://login.cchaxcess.com/ps/auth/v1.0/core/connect"
        ),
        api_base=os.environ.get("CCH_OIP_API_BASE", "https://api.cchaxcess.com"),
        token_cache_path=Path(
            os.environ.get("CCH_OIP_TOKEN_CACHE", str(_PACKAGE_ROOT / ".token_cache.json"))
        ),
    )
