from fastapi import APIRouter, HTTPException

from integrations.crm_client import CRMClient
from services.lead_scorer import score_lead
from services.analytics_service import SCRAPED_LEADS

router = APIRouter(tags=["Scoring"])


def _extract_lead_record(response: dict) -> dict:
    if not response.get("success"):
        return None

    data = response.get("data") or {}
    if isinstance(data.get("lead"), dict):
        return data["lead"]
    if isinstance(data, dict) and data.get("sf_id"):
        return data
    return data if isinstance(data, dict) else None


@router.post("/score/{lead_id}")
def score_single_lead(lead_id: str, update_dashboard: bool = True):
    """
    Fetch one lead from CRM by ID, score it, and return the result.
    Use this for testing without running a full batch sync.

    lead_id: Togile sf_id (e.g. 518029) or CRM _id string.
    """
    client = CRMClient.from_settings()
    response = client.fetch_lead(lead_id)
    lead = _extract_lead_record(response)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=response.get("message") or response.get("error") or f"Lead {lead_id} not found",
        )

    result = score_lead(lead)

    if update_dashboard:
        existing = next(
            (i for i, row in enumerate(SCRAPED_LEADS) if row["lead_id"] == result["lead_id"]),
            None,
        )
        dashboard_row = {
            "lead_id": result["lead_id"],
            "name": result["name"],
            "company": result["company"],
            "score": result["score"],
            "label": result["label"],
            "ml_probability": result["ml_probability"],
        }
        if existing is not None:
            SCRAPED_LEADS[existing] = dashboard_row
        else:
            SCRAPED_LEADS.append(dashboard_row)

    return result
