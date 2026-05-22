import joblib
import logging
from datetime import datetime
from ml_pipeline.model_registry import get_active_model
from ml_pipeline.feature_store import prepare_features

logger = logging.getLogger(__name__)

def calculate_ml_score(lead_data: dict) -> float:
    """
    Returns ML probability (0-100) using ONLY raw lead attributes.
    ✅ NO rule_score injection — guaranteed independence.
    """
    active = get_active_model()
    if not active:
        logger.warning("⚠️ No active model. Returning fallback score 50.0")
        return 50.0

    try:
        pipeline = joblib.load(active["path"])
        
        # Normalize input for feature extraction
        features = {
            "industry": str(lead_data.get("industry", "unknown")).strip() or "unknown",
            "lead_source": str(lead_data.get("lead_source", "unknown")).strip() or "unknown",
            "company_size": float(lead_data.get("company_size", 0) or 0),
            "estimated_budget": float(lead_data.get("estimated_budget", 0) or 0),
            "days_since_first_contact": int(lead_data.get("days_since_first_contact", 0) or 0)
        }
        
        X = prepare_features(features)
        prob = pipeline.predict_proba(X)[0][1]
        score = round(float(prob) * 100, 2)
        
        # 🔍 Independence verification log
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"🔍 ML Score: {score} | Input: {features}")
        
        return score
        
    except Exception as e:
        logger.error(f"❌ ML prediction failed: {e}")
        return 50.0  # Safe fallback