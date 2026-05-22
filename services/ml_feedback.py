import pandas as pd
import logging
from ml_pipeline.config import OUTCOMES_FILE

logger = logging.getLogger(__name__)

def record_outcome(outcome_data: dict) -> bool:
    """
    Appends outcome to outcomes.csv for future training.
    Required keys: lead_id, converted (0/1), lost (0/1)
    """
    try:
        required = ["lead_id", "converted", "lost"]
        if not all(k in outcome_data for k in required):
            logger.error(f"Missing required keys in outcome: {outcome_data.keys()}")
            return False
        
        new_row = pd.DataFrame([{
            "lead_id": int(outcome_data["lead_id"]),
            "contacted": bool(outcome_data.get("contacted", False)),
            "replied": bool(outcome_data.get("replied", False)),
            "meeting_booked": bool(outcome_data.get("meeting_booked", False)),
            "converted": int(outcome_data["converted"]),
            "lost": int(outcome_data["lost"]),
            "revenue": float(outcome_data.get("revenue") or 0),
            "recorded_at": pd.Timestamp.now().isoformat()
        }])
        
        if OUTCOMES_FILE.exists():
            new_row.to_csv(OUTCOMES_FILE, mode="a", header=False, index=False)
        else:
            new_row.to_csv(OUTCOMES_FILE, index=False)
        
        logger.info(f"📥 Outcome recorded for lead {outcome_data['lead_id']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to record outcome: {e}")
        return False