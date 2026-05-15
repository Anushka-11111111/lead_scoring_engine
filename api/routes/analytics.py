from fastapi import APIRouter

from services.analytics_service import (
    SCRAPED_LEADS,
    SCRAPE_STATUS
)

router = APIRouter()


@router.get("/analytics")
def analytics():

    total = len(SCRAPED_LEADS)

    hot = len([
        x for x in SCRAPED_LEADS
        if x["score"] >= 80
    ])

    warm = len([
        x for x in SCRAPED_LEADS
        if 50 <= x["score"] < 80
    ])

    cold = len([
        x for x in SCRAPED_LEADS
        if x["score"] < 50
    ])

    avg = 0

    if total > 0:
        avg = round(
            sum(x["score"] for x in SCRAPED_LEADS) / total,
            1
        )

    top_leads = sorted(
        SCRAPED_LEADS,
        key=lambda x: x["score"],
        reverse=True
    )[:10]

    return {
        "total_leads": total,
        "hot_leads": hot,
        "warm_leads": warm,
        "cold_leads": cold,
        "average_score": avg,
        "top_leads": top_leads,
        "status": SCRAPE_STATUS
    }