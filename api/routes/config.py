from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from integrations.crm_client import CRMClient
from services.crm_config_store import (
    CRMNotConfiguredError,
    get_crm_config_status,
    get_crm_credentials,
    set_crm_credentials,
)

router = APIRouter(tags=["Config"])


class CrmConfigRequest(BaseModel):
    base_url: str = Field(..., min_length=1, description="CRM API base URL")
    api_key: str = Field(default="", description="CRM API key")
    secret_key: str = Field(default="", description="CRM secret key")
    origin: str = Field(..., min_length=1, description="CRM origin header value")


def _resolve_credentials(body: CrmConfigRequest) -> dict:
    existing = get_crm_credentials() or {}
    api_key = body.api_key.strip() or existing.get("api_key", "")
    secret_key = body.secret_key.strip() or existing.get("secret_key", "")

    if not api_key or not secret_key:
        raise HTTPException(
            status_code=400,
            detail="API key and secret key are required.",
        )

    return {
        "base_url": body.base_url,
        "api_key": api_key,
        "secret_key": secret_key,
        "origin": body.origin,
    }


@router.get("/config/crm")
def get_crm_config():
    return get_crm_config_status()


@router.post("/config/crm")
def save_crm_config(body: CrmConfigRequest):
    values = _resolve_credentials(body)
    set_crm_credentials(**values)
    return {
        "message": "CRM configuration saved",
        **get_crm_config_status(),
    }


@router.post("/config/crm/test")
def test_crm_config(body: CrmConfigRequest):
    values = _resolve_credentials(body)
    client = CRMClient(**values)
    response = client.fetch_leads_table(page=1, quantity=1)

    if not isinstance(response, dict) or not response.get("success", False):
        detail = response.get("message") or response.get("error") or "CRM connection failed"
        raise HTTPException(status_code=400, detail=detail)

    return {"message": "CRM connection successful", "success": True}


def require_crm_client() -> CRMClient:
    try:
        return CRMClient.from_settings()
    except CRMNotConfiguredError as exc:
        raise HTTPException(status_code=412, detail=str(exc)) from exc
