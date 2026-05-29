# integrations/crm_client.py

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class CRMClient:
    """
    Togile CRM API client using api-key / secret-key authentication.
    No login tokens or session cookies required.
    """

    LEADS_TABLE_PATH = "/api/v1/leads/table"

    def __init__(
        self,
        base_url: str,
        api_key: str,
        secret_key: str,
        origin: str,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        origin_value = origin.rstrip("/") if origin else origin

        self._json_headers = {
            "api-key": api_key,
            "secret-key": secret_key,
            "origin": origin_value,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._read_headers = {
            "api-key": api_key,
            "secret-key": secret_key,
            "origin": origin_value,
            "Accept": "application/json",
        }

    @classmethod
    def from_settings(cls) -> "CRMClient":
        from core_contracts.settings import settings

        return cls(
            base_url=settings.CRM_BASE_URL,
            api_key=settings.CRM_API_KEY,
            secret_key=settings.CRM_SECRET_KEY,
            origin=settings.CRM_ORIGIN,
        )

    def put(self, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.put(
                    url,
                    headers=self._json_headers,
                    json=payload or {},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "CRM PUT %s failed (%s): %s",
                url,
                exc.response.status_code,
                exc.response.text[:500],
            )
            return {
                "success": False,
                "error": str(exc),
                "status_code": exc.response.status_code,
            }
        except Exception as exc:
            logger.error("CRM PUT %s failed: %s", url, exc)
            return {"success": False, "error": str(exc)}

    def get(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=self._read_headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "CRM GET %s failed (%s): %s",
                url,
                exc.response.status_code,
                exc.response.text[:500],
            )
            return {
                "success": False,
                "error": str(exc),
                "status_code": exc.response.status_code,
            }
        except Exception as exc:
            logger.error("CRM GET %s failed: %s", url, exc)
            return {"success": False, "error": str(exc)}

    def fetch_leads_table(
        self,
        page: int = 1,
        quantity: int = 50,
        sort_field: str = "sf_created_at",
        is_ascending: bool = False,
        **extra: Any,
    ) -> Dict[str, Any]:
        payload = {
            "page": page,
            "quantity": quantity,
            "sortField": sort_field,
            "isAscending": is_ascending,
            **extra,
        }
        return self.put(self.LEADS_TABLE_PATH, payload)

    def fetch_lead(self, lead_id: str) -> Dict[str, Any]:
        return self.get(f"/api/v1/leads/{lead_id}")
