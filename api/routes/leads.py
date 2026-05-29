from fastapi import APIRouter, HTTPException

from integrations.crm_client import CRMClient
from api.routes.score import _extract_lead_record
from services.analytics_service import SCRAPED_LEADS
from services.lead_scorer import score_lead
from services.lead_details import format_crm_details

router = APIRouter(tags=["Leads"])


@router.get("/leads")
def get_all_leads():
    leads = sorted(SCRAPED_LEADS, key=lambda x: x.get("score", 0), reverse=True)
    return {
        "total": len(leads),
        "leads": leads,
    }


@router.get("/leads/{lead_id}")
def get_lead_detail(lead_id: str):
    client = CRMClient.from_settings()
    response = client.fetch_lead(lead_id)
    lead = _extract_lead_record(response)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=response.get("message") or f"Lead {lead_id} not found",
        )

    scored = score_lead(lead)
    crm_details = format_crm_details(lead)

    return {
        **scored,
        "crm_details": crm_details,
    }
