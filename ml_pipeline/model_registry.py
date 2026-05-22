import json
import logging
from datetime import datetime
from pathlib import Path
from ml_pipeline.config import MODELS_DIR

logger = logging.getLogger(__name__)
REGISTRY_FILE = MODELS_DIR / "model_registry.json"

def _read_registry() -> dict:
    if not REGISTRY_FILE.exists():
        return {"versions": [], "active_version": None}
    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)

def _write_registry(registry: dict):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)

def register_model(version: str, path: str, metrics: dict) -> dict:
    registry = _read_registry()
    entry = {
        "version": version,
        "path": path,
        "metrics": metrics,
        "created_at": datetime.utcnow().isoformat()
    }
    registry["versions"].append(entry)
    _write_registry(registry)
    logger.info(f"📦 Registered model {version}")
    return entry

def activate_model(version: str) -> str:
    registry = _read_registry()

    versions = registry.get("versions", [])

    model = next((v for v in versions if v["version"] == version), None)

    if not model:
        raise ValueError(f"Version {version} not found")

    registry["active_version"] = version
    _write_registry(registry)

    logger.info(f"🚀 Activated model {version}")
    return version

def get_active_model() -> dict | None:
    registry = _read_registry()

    versions = registry.get("versions", [])

    if not versions:
        return None

    active_version = registry.get("active_version")

    # --------------------------------------------------
    # If active version missing → fallback to latest
    # --------------------------------------------------
    if not active_version:
        latest = versions[-1]
        registry["active_version"] = latest["version"]
        _write_registry(registry)
        return latest

    return next(
        (v for v in versions if v["version"] == active_version),
        None
    )

def get_latest_model() -> dict | None:
    registry = _read_registry()
    versions = registry.get("versions", [])
    return versions[-1] if versions else None

def list_models() -> list[dict]:
    return _read_registry()["versions"]