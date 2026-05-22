import logging
import numpy as np
import pandas as pd

from typing import Dict, Any

from ml_pipeline.model_registry import get_active_model
from ml_pipeline.feature_store import prepare_features

logger = logging.getLogger(__name__)


class MLRefinementLayer:
    """
    Hybrid ML refinement engine (registry-based version).

    - Uses model registry (NO hardcoded joblib files)
    - Works with dynamically trained CRM models
    - Safe fallback to rule-based scoring
    """

    def __init__(self):
        self._model = None
        self._pipeline = None
        self._load_from_registry()

    # ======================================================
    # LOAD MODEL FROM REGISTRY (NOT FILE SYSTEM)
    # ======================================================
    def _load_from_registry(self):
        try:
            active = get_active_model()

            if not active:
                logger.warning("⚠️ No active model found (ML disabled)")
                self._pipeline = None
                return

            import joblib

            self._pipeline = joblib.load(active["path"])

            logger.info(
                f"✅ ML Refinement Layer loaded from registry: {active['version']}"
            )

        except Exception as e:
            logger.warning(f"⚠️ Failed to load model from registry: {e}")
            self._pipeline = None

    # ======================================================
    # MAIN REFINEMENT FUNCTION
    # ======================================================
    def refine(
        self,
        lead_data: Dict[str, Any],
        rule_score: float,
        debug: bool = False
    ) -> Dict[str, Any]:

        # --------------------------------------------------
        # SAFE FALLBACK (NO MODEL)
        # --------------------------------------------------
        if self._pipeline is None:
            return {
                "ml_score": rule_score,
                "ml_prediction": int(rule_score >= 50),
                "ml_probability": rule_score / 100.0,
                "confidence": 0.5,
                "warning": "ML not loaded (using rule-based only)"
            }

        try:
            # --------------------------------------------------
            # FEATURE PREPARATION
            # --------------------------------------------------
            X = prepare_features(
                lead_data,
                self._pipeline.named_steps["preprocessor"]
            )

            # --------------------------------------------------
            # PREDICTION
            # --------------------------------------------------
            prob = self._pipeline.predict_proba(X)[0][1]

            score = round(float(prob) * 100, 2)

            # --------------------------------------------------
            # DEBUG
            # --------------------------------------------------
            if debug:
                logger.info(f"📊 ML Probability: {prob:.4f} | Rule Score: {rule_score}")

            # --------------------------------------------------
            # FINAL OUTPUT
            # --------------------------------------------------
            return {
                "ml_score": score,
                "ml_prediction": int(prob >= 0.3),
                "ml_probability": round(float(prob), 4),
                "confidence": round(1 - abs(0.5 - prob), 4)
            }

        except Exception as e:
            logger.warning(f"⚠️ ML refinement failed: {e}")

            return {
                "ml_score": rule_score,
                "ml_prediction": int(rule_score >= 50),
                "ml_probability": rule_score / 100.0,
                "confidence": 0.5,
                "warning": str(e)
            }