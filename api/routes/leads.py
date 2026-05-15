from fastapi import APIRouter

from state.runtime_store import SCRAPED_LEADS

router = APIRouter()


@router.get("/leads")
def get_leads():

    return {
        "total": len(SCRAPED_LEADS),
        "leads": SCRAPED_LEADS
    }