from fastapi import APIRouter, HTTPException

from api.routes.config import require_crm_client
from services.lead_scorer import score_lead
from services.analytics_service import SCRAPED_LEADS
from services.ml_service import maybe_trigger_training

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
    client = require_crm_client()
    response = client.fetch_lead(lead_id)
    lead = _extract_lead_record(response)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=response.get("message") or response.get("error") or f"Lead {lead_id} not found",
        )

    result = score_lead(lead)

    maybe_trigger_training()

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
            "ml_score": result.get("ml_score"),
            "ml_probability": result.get("ml_probability"),
            "ml_label": result.get("ml_label"),
            "ml_active": result.get("ml_active", False),
            "ml_warning": result.get("ml_warning"),
        }
        if existing is not None:
            SCRAPED_LEADS[existing] = dashboard_row
        else:
            SCRAPED_LEADS.append(dashboard_row)

    return result
