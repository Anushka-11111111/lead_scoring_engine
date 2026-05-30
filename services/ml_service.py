import json
import logging
import threading
from datetime import datetime
from typing import Any, Dict, Optional

import joblib
import pandas as pd

from ml_pipeline.config import (
    LEADS_FILE,
    OUTCOMES_FILE,
    TRAINING_CONFIG,
    TRAINING_STATE_FILE,
)
from ml_pipeline.feature_store import prepare_features
from ml_pipeline.model_registry import get_active_model
from ml_pipeline.train_model import run_training

logger = logging.getLogger(__name__)

_pipeline_cache = None
_active_version: Optional[str] = None
_training_lock = threading.Lock()
_training_in_progress = False

DEFAULT_STATE = {
    "completed_leads": 0,
    "seen_lead_ids": [],
    "last_training_at": None,
    "last_training_count": 0,
}


def _load_state() -> dict:
    if not TRAINING_STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    try:
        data = json.loads(TRAINING_STATE_FILE.read_text(encoding="utf-8"))
        for key, value in DEFAULT_STATE.items():
            data.setdefault(key, value)
        return data
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_STATE)


def _save_state(state: dict) -> None:
    TRAINING_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRAINING_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _first_value(observations: Dict[str, Any], *keys: str, default=None):
    for key in keys:
        value = observations.get(key)
        if value not in (None, "", "unknown", "null"):
            return value
    return default


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def extract_ml_features(
    observations: Dict[str, Any],
    lead: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    lead = lead or {}
    created_at = _first_value(
        observations,
        "created_at",
        "sf_created_at",
        "createdAt",
        default=lead.get("sf_created_at") or lead.get("created_at"),
    )

    days_since = _to_int(
        _first_value(observations, "days_since_first_contact", default=0)
    )
    if days_since == 0 and created_at:
        try:
            created = pd.to_datetime(created_at, errors="coerce")
            if pd.notna(created):
                days_since = max(0, (pd.Timestamp.now() - created).days)
        except Exception:
            days_since = 0

    return {
        "industry": str(
            _first_value(
                observations,
                "industry",
                "sf_industry",
                "company.industry",
                default="unknown",
            )
            or "unknown"
        ).strip()
        or "unknown",
        "lead_source": str(
            _first_value(
                observations,
                "lead_source",
                "sf_lead_source",
                "source",
                "sf_source",
                default="unknown",
            )
            or "unknown"
        ).strip()
        or "unknown",
        "company_size": _to_float(
            _first_value(
                observations,
                "company_size",
                "employee_count",
                "sf_employee_count",
                "employees",
                "sf_company_size",
                default=0,
            )
        ),
        "estimated_budget": _to_float(
            _first_value(
                observations,
                "estimated_budget",
                "annual_revenue",
                "sf_annual_revenue",
                "budget",
                "sf_budget",
                default=0,
            )
        ),
        "days_since_first_contact": days_since,
    }


def count_completed_leads() -> int:
    return int(_load_state().get("completed_leads", 0))


def _proxy_outcome(rule_score: float, label: str) -> Dict[str, int]:
    normalized = (label or "").lower()
    if rule_score >= 80 or "hot" in normalized:
        return {"converted": 1, "lost": 0}
    if rule_score < 50 or "cold" in normalized:
        return {"converted": 0, "lost": 1}
    return {"converted": 1 if rule_score >= 50 else 0, "lost": 0}


def _append_training_row(lead_id: str, features: Dict[str, Any], rule_score: float, label: str) -> None:
    lead_row = {
        "lead_id": lead_id,
        **features,
        "created_at": datetime.utcnow().isoformat(),
    }
    outcome = _proxy_outcome(rule_score, label)
    outcome_row = {
        "lead_id": lead_id,
        "contacted": True,
        "replied": rule_score >= 50,
        "meeting_booked": rule_score >= 70,
        **outcome,
        "revenue": 0.0,
        "recorded_at": datetime.utcnow().isoformat(),
    }

    lead_df = pd.DataFrame([lead_row])
    outcome_df = pd.DataFrame([outcome_row])

    if LEADS_FILE.exists():
        existing = pd.read_csv(LEADS_FILE)
        if "lead_id" in existing.columns and str(lead_id) in existing["lead_id"].astype(str).values:
            existing = existing[existing["lead_id"].astype(str) != str(lead_id)]
            existing = pd.concat([existing, lead_df], ignore_index=True)
            existing.to_csv(LEADS_FILE, index=False)
        else:
            lead_df.to_csv(LEADS_FILE, mode="a", header=False, index=False)
    else:
        lead_df.to_csv(LEADS_FILE, index=False)

    if OUTCOMES_FILE.exists():
        existing = pd.read_csv(OUTCOMES_FILE)
        if "lead_id" in existing.columns and str(lead_id) in existing["lead_id"].astype(str).values:
            existing = existing[existing["lead_id"].astype(str) != str(lead_id)]
            existing = pd.concat([existing, outcome_df], ignore_index=True)
            existing.to_csv(OUTCOMES_FILE, index=False)
        else:
            outcome_df.to_csv(OUTCOMES_FILE, mode="a", header=False, index=False)
    else:
        outcome_df.to_csv(OUTCOMES_FILE, index=False)


def record_completed_lead(
    lead_id: str,
    observations: Dict[str, Any],
    rule_score: float,
    label: str,
    lead: Optional[Dict[str, Any]] = None,
) -> int:
    state = _load_state()
    seen = {str(item) for item in state.get("seen_lead_ids", [])}

    features = extract_ml_features(observations, lead)
    _append_training_row(str(lead_id), features, rule_score, label)

    if str(lead_id) not in seen:
        seen.add(str(lead_id))
        state["completed_leads"] = int(state.get("completed_leads", 0)) + 1
        state["seen_lead_ids"] = sorted(seen)
        _save_state(state)

    return int(state["completed_leads"])


def _confidence_level(probability: float) -> str:
    distance = abs(0.5 - probability)
    if distance >= 0.35:
        return "High"
    if distance >= 0.15:
        return "Medium"
    return "Low"


def _ml_label(score: float) -> str:
    if score >= 80:
        return "Hot Lead"
    if score >= 50:
        return "Warm Lead"
    return "Cold Lead"


def _build_reasoning(features: Dict[str, Any], probability: float, ml_score: float) -> str:
    reasons = []

    industry = features.get("industry", "unknown")
    source = features.get("lead_source", "unknown")
    company_size = features.get("company_size", 0)
    budget = features.get("estimated_budget", 0)
    age = features.get("days_since_first_contact", 0)

    if industry != "unknown":
        reasons.append(f"Industry ({industry}) contributed to the conversion estimate.")
    if source != "unknown":
        reasons.append(f"Lead source ({source}) influenced the model's prediction.")
    if company_size >= 200:
        reasons.append("Large company size signals stronger fit in historical outcomes.")
    elif company_size >= 50:
        reasons.append("Mid-size company profile is moderately favorable.")
    elif company_size > 0:
        reasons.append("Smaller company size slightly reduced predicted conversion odds.")
    if budget >= 100000:
        reasons.append("High estimated budget increased predicted conversion likelihood.")
    elif budget > 0:
        reasons.append("Budget level was factored into the conversion estimate.")
    if age <= 3:
        reasons.append("Very recent lead activity suggests higher engagement potential.")
    elif age >= 30:
        reasons.append("Older lead age reduced the model's confidence in fast conversion.")

    if probability >= 0.75:
        reasons.append("Overall, the model sees strong conversion potential independent of rule scoring.")
    elif probability >= 0.5:
        reasons.append("Overall, the model predicts moderate conversion potential.")
    else:
        reasons.append("Overall, the model predicts lower conversion potential than average.")

    reasons.append(f"Independent ML score: {ml_score:.1f}/100.")
    return " ".join(reasons)


def _training_warning(completed: int, model_loaded: bool) -> Optional[str]:
    min_train = TRAINING_CONFIG["min_labeled_samples"]
    min_mature = TRAINING_CONFIG["min_mature_samples"]

    if completed < min_train:
        return (
            f"ML training has not started yet ({completed}/{min_train} completed leads). "
            "Scores below are rule-based until training begins."
        )

    if not model_loaded:
        return (
            f"ML model is training or unavailable ({completed} completed leads). "
            "Independent ML scores will appear once training finishes."
        )

    if completed < min_mature:
        return (
            f"Model is still under training ({completed}/{min_mature} completed leads). "
            "ML scores are available but may be unreliable until more outcomes are collected."
        )

    return None


def get_ml_status() -> Dict[str, Any]:
    completed = count_completed_leads()
    active = get_active_model()
    model_loaded = active is not None
    warning = _training_warning(completed, model_loaded)

    return {
        "completed_leads": completed,
        "training_threshold": TRAINING_CONFIG["min_labeled_samples"],
        "mature_threshold": TRAINING_CONFIG["min_mature_samples"],
        "model_loaded": model_loaded,
        "model_version": active["version"] if active else None,
        "training_in_progress": _training_in_progress,
        "warning": warning,
        "ready_for_training": completed >= TRAINING_CONFIG["min_labeled_samples"],
        "mature": completed >= TRAINING_CONFIG["min_mature_samples"],
    }


def _get_pipeline():
    global _pipeline_cache, _active_version

    active = get_active_model()
    if not active:
        _pipeline_cache = None
        _active_version = None
        return None

    if active["version"] != _active_version:
        _pipeline_cache = joblib.load(active["path"])
        _active_version = active["version"]
        logger.info("Loaded ML model %s", active["version"])

    return _pipeline_cache


def invalidate_model_cache() -> None:
    global _pipeline_cache, _active_version
    _pipeline_cache = None
    _active_version = None


def score_with_ml(
    observations: Dict[str, Any],
    rule_score: float,
    label: str,
    lead: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    completed = count_completed_leads()
    features = extract_ml_features(observations, lead)
    min_train = TRAINING_CONFIG["min_labeled_samples"]
    pipeline = _get_pipeline() if completed >= min_train else None
    warning = _training_warning(completed, pipeline is not None)

    if pipeline is None:
        if completed >= min_train:
            reasoning = (
                "ML model is training or not ready yet. "
                "An independent score will appear after training completes."
            )
        else:
            reasoning = (
                f"ML has not produced an independent score yet ({completed}/{min_train} completed leads). "
                "Keep syncing leads to start training."
            )
        return {
            "ml_score": None,
            "ml_probability": None,
            "ml_label": None,
            "ml_confidence_level": "Low",
            "ml_reasoning": reasoning,
            "ml_warning": warning,
            "ml_active": False,
        }

    try:
        frame = prepare_features(features)
        probability = float(pipeline.predict_proba(frame)[0][1])
        ml_score = round(probability * 100, 1)

        return {
            "ml_score": ml_score,
            "ml_probability": round(probability * 100, 1),
            "ml_label": _ml_label(ml_score),
            "ml_confidence_level": _confidence_level(probability),
            "ml_reasoning": _build_reasoning(features, probability, ml_score),
            "ml_warning": warning,
            "ml_active": True,
        }
    except Exception as exc:
        logger.warning("ML scoring failed: %s", exc)
        return {
            "ml_score": None,
            "ml_probability": None,
            "ml_label": None,
            "ml_confidence_level": "Low",
            "ml_reasoning": f"ML prediction failed: {exc}",
            "ml_warning": warning or "ML prediction failed; rule-based score is shown instead.",
            "ml_active": False,
        }


def maybe_trigger_training() -> None:
    completed = count_completed_leads()
    if completed < TRAINING_CONFIG["min_labeled_samples"]:
        return

    state = _load_state()
    last_count = int(state.get("last_training_count", 0))
    if completed == last_count and _get_pipeline() is not None:
        return

    def _train():
        global _training_in_progress
        with _training_lock:
            if _training_in_progress:
                return
            _training_in_progress = True
        try:
            result = run_training()
            if result:
                invalidate_model_cache()
                state = _load_state()
                state["last_training_at"] = datetime.utcnow().isoformat()
                state["last_training_count"] = completed
                _save_state(state)
                logger.info("ML training finished: %s", result["version"])
        finally:
            _training_in_progress = False

    thread = threading.Thread(target=_train, daemon=True)
    thread.start()
