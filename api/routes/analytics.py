from fastapi import APIRouter

from services.analytics_service import (
    SCRAPED_LEADS,
    SCRAPE_STATUS
)

router = APIRouter()

SCORE_BRACKETS = [
    ("0-19", 0, 19),
    ("20-39", 20, 39),
    ("40-59", 40, 59),
    ("60-79", 60, 79),
    ("80-100", 80, 100),
]


def _score_distribution(leads: list) -> list:
    distribution = []
    for label, low, high in SCORE_BRACKETS:
        in_bracket = [
            lead for lead in leads
            if low <= lead.get("score", 0) <= high
        ]
        companies = {
            (lead.get("company") or "Unknown Company").strip()
            for lead in in_bracket
        }
        distribution.append({
            "bracket": label,
            "leads": len(in_bracket),
            "companies": len(companies),
        })
    return distribution


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
        "score_distribution": _score_distribution(SCRAPED_LEADS),
        "status": SCRAPE_STATUS
    }