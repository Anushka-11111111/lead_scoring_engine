import httpx
import logging
from core_contracts.settings import settings

logger = logging.getLogger(__name__)

def sync_crm_outcomes_to_ml() -> dict:
    """
    Polls your CRM for closed leads and pushes them to /ml/outcome.
    Uses your existing integrations.crm_client if available.
    """
    try:
        # 🔌 Use your existing CRM client from integrations/
        from integrations.crm_client import CRMClient
        client = CRMClient()
        closed_leads = client.get_closed_leads(limit=100)
        
        if not closed_leads:
            logger.info("📭 No closed leads from CRM. Skipping sync.")
            return {"success": 0, "failed": 0}
        
        success, failed = 0, 0
        for lead in closed_leads:
            try:
                # Map CRM response → ML outcome format
                payload = {
                    "lead_id": int(lead.get("id") or lead.get("lead_id")),
                    "converted": 1 if lead.get("status") in ["won", "closed_won", "converted"] else 0,
                    "lost": 1 if lead.get("status") in ["lost", "closed_lost"] else 0,
                    "revenue": float(lead.get("deal_value") or lead.get("revenue") or 0),
                    "contacted": bool(lead.get("contacted", False)),
                    "replied": bool(lead.get("replied", False)),
                    "meeting_booked": bool(lead.get("meeting_booked", False))
                }
                
                resp = httpx.post(
                    "http://localhost:8000/ml/outcome",
                    json=payload,
                    timeout=5.0,
                    headers={"Authorization": f"Bearer {settings.CRM_API_KEY}"}
                )
                resp.raise_for_status()
                success += 1
                
            except Exception as e:
                failed += 1
                logger.warning(f"Failed to sync lead {lead.get('id')}: {e}")
        
        logger.info(f"📤 Synced {success} outcomes to ML. Failed: {failed}")
        return {"success": success, "failed": failed}
        
    except ImportError:
        logger.warning("⚠️ integrations.crm_client not found. Skipping CRM sync.")
        return {"success": 0, "failed": 0}
    except Exception as e:
        logger.error(f"CRM sync crashed: {e}")
        return {"success": 0, "failed": len(closed_leads) if 'closed_leads' in locals() else 0}