import joblib
import logging

from ml_pipeline.model_registry import get_active_model
from ml_pipeline.feature_store import prepare_features
from ml_pipeline.train_model import train_model  # fallback training

logger = logging.getLogger(__name__)


def _load_pipeline(model_path: str):
    return joblib.load(model_path)


def predict_lead_score(lead_data: dict) -> float:
    """
    Returns: score (0–100)
    """

    active = get_active_model()

    # --------------------------------------------------
    # 🚨 COLD START HANDLING
    # --------------------------------------------------
    if not active:
        logger.warning("⚠️ No active model found. Training new model...")

        model_meta = train_model()

        active = {
            "path": model_meta["model_path"]
        }

    # --------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------
    pipeline = _load_pipeline(active["path"])

    # --------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------
    X = prepare_features(
        lead_data,
        pipeline.named_steps["preprocessor"]
    )

    # --------------------------------------------------
    # PREDICTION
    # --------------------------------------------------
    prob = pipeline.predict_proba(X)[0][1]

    score = round(float(prob) * 100, 2)

    logger.info(f"📊 Lead score: {score}")

    return score