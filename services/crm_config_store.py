import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "crm_config.json"

_lock = threading.Lock()
_config: Optional[Dict[str, str]] = None


class CRMNotConfiguredError(Exception):
    """Raised when CRM credentials have not been set."""


def _mask_secret(value: str) -> str:
    if not value or len(value) < 8:
        return "****"
    return f"{value[:4]}...{value[-4:]}"


def _normalize(values: Dict[str, str]) -> Dict[str, str]:
    return {
        "base_url": values["base_url"].strip().rstrip("/"),
        "api_key": values["api_key"].strip(),
        "secret_key": values["secret_key"].strip(),
        "origin": values["origin"].strip().rstrip("/"),
    }


def _is_complete(values: Optional[Dict[str, str]]) -> bool:
    if not values:
        return False
    return all(values.get(key) for key in ("base_url", "api_key", "secret_key", "origin"))


def _load_from_file() -> Optional[Dict[str, str]]:
    if not CONFIG_PATH.exists():
        return None
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return None
        return _normalize(raw)
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return None


def _load_from_env() -> Optional[Dict[str, str]]:
    from core_contracts.settings import settings

    values = {
        "base_url": settings.CRM_BASE_URL,
        "api_key": settings.CRM_API_KEY,
        "secret_key": settings.CRM_SECRET_KEY,
        "origin": settings.CRM_ORIGIN,
    }
    if not _is_complete(values):
        return None
    return _normalize(values)


def _persist(values: Dict[str, str]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(values, indent=2), encoding="utf-8")


def init_crm_config() -> None:
    global _config
    with _lock:
        _config = _load_from_file() or _load_from_env()


def get_crm_credentials() -> Optional[Dict[str, str]]:
    with _lock:
        if _config is None:
            init_crm_config()
        return dict(_config) if _config else None


def is_crm_configured() -> bool:
    return _is_complete(get_crm_credentials())


def set_crm_credentials(
    base_url: str,
    api_key: str,
    secret_key: str,
    origin: str,
) -> Dict[str, str]:
    global _config
    values = _normalize(
        {
            "base_url": base_url,
            "api_key": api_key,
            "secret_key": secret_key,
            "origin": origin,
        }
    )
    with _lock:
        _config = values
        _persist(values)
    return values


def get_crm_config_status() -> Dict[str, Any]:
    creds = get_crm_credentials()
    configured = _is_complete(creds)
    if not configured:
        return {"configured": False}

    return {
        "configured": True,
        "base_url": creds["base_url"],
        "origin": creds["origin"],
        "api_key_hint": _mask_secret(creds["api_key"]),
        "secret_key_hint": _mask_secret(creds["secret_key"]),
    }
