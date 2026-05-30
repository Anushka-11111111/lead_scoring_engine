from services.lead_scorer import score_lead
from services.analytics_service import (
    SCRAPED_LEADS,
    SCRAPE_STATUS
)
from services.ml_service import maybe_trigger_training


def run(leads, pusher=None):

    print("AI ENGINE STARTED")

    # =========================
    # RESET DASHBOARD STATE
    # =========================
    SCRAPED_LEADS.clear()

    SCRAPE_STATUS["running"] = True
    SCRAPE_STATUS["completed"] = False
    SCRAPE_STATUS["processed"] = 0
    SCRAPE_STATUS["total"] = len(leads)

    processed = 0

    for lead in leads:
        try:
            scored = score_lead(lead)
            lead_id = scored["lead_id"]

            if pusher:
                try:
                    pusher.push_score(lead_id, scored["crm_payload"])
                except Exception as e:
                    print(f"Push failed for {lead_id}: {e}")

            SCRAPED_LEADS.append({
                "lead_id": scored["lead_id"],
                "name": scored["name"],
                "company": scored["company"],
                "score": scored["score"],
                "label": scored["label"],
                "ml_score": scored.get("ml_score"),
                "ml_probability": scored.get("ml_probability"),
                "ml_label": scored.get("ml_label"),
                "ml_active": scored.get("ml_active", False),
                "ml_warning": scored.get("ml_warning"),
            })

            processed += 1
            SCRAPE_STATUS["processed"] = processed

            print(
                f"OK {scored['name']} | "
                f"{scored['company']} | "
                f"Score: {scored['score']}"
            )

        except Exception as e:
            lead_id = str(
                lead.get("id") or lead.get("_id") or lead.get("sf_id") or "unknown"
            )
            print(f"Lead failed {lead_id}: {e}")

    # =========================
    # FINAL STATUS
    # =========================
    SCRAPE_STATUS["running"] = False
    SCRAPE_STATUS["completed"] = True

    maybe_trigger_training()

    print(f"TOTAL PROCESSED: {processed}")

    return processed