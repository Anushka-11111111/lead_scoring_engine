import pandas as pd
import joblib
import logging
from datetime import datetime

from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split

from ml_pipeline.config import *
from ml_pipeline.model_registry import register_model, activate_model

logger = logging.getLogger(__name__)


# ======================================================
# LOAD DATA
# ======================================================
def load_training_data() -> pd.DataFrame:
    """Loads leads + outcomes and prepares training dataset."""

    if not LEADS_FILE.exists() or not OUTCOMES_FILE.exists():
        return pd.DataFrame()

    leads = pd.read_csv(LEADS_FILE)
    outcomes = pd.read_csv(OUTCOMES_FILE)

    if leads.empty or outcomes.empty:
        return pd.DataFrame()

    merged = pd.merge(leads, outcomes, on="lead_id", how="inner")

    # Only definitive labels
    labeled = merged[(merged["converted"] == 1) | (merged["lost"] == 1)].copy()

    if labeled.empty:
        return pd.DataFrame()

    # Feature engineering
    if "created_at" in labeled.columns:
        labeled["created_at"] = pd.to_datetime(labeled["created_at"], errors="coerce")

        labeled["days_since_first_contact"] = (
            pd.Timestamp.now() - labeled["created_at"]
        ).dt.days.fillna(0).astype(int)

    for col in NUMERIC_FEATURES:
        if col in labeled.columns:
            labeled[col] = pd.to_numeric(labeled[col], errors="coerce").fillna(0.0)

    for col in CATEGORICAL_FEATURES:
        if col in labeled.columns:
            labeled[col] = labeled[col].astype(str).str.strip().replace("", "unknown")

    if "days_since_first_contact" in labeled.columns:
        labeled["lead_age_bucket"] = pd.cut(
            labeled["days_since_first_contact"],
            bins=[-1, 3, 7, 14, 30, 999],
            labels=["0-3", "4-7", "8-14", "15-30", "30+"],
        ).astype(str)

    if "estimated_budget" in labeled.columns and "company_size" in labeled.columns:
        labeled["budget_per_size"] = (
            labeled["estimated_budget"] / (labeled["company_size"] + 1)
        )

    required_cols = CATEGORICAL_FEATURES + NUMERIC_FEATURES + ["converted"]

    available = [c for c in required_cols if c in labeled.columns]

    if "converted" not in available:
        return pd.DataFrame()

    return labeled[available].dropna(subset=["converted"])


# ======================================================
# TRAIN MODEL
# ======================================================
def run_training() -> dict | None:

    df = load_training_data()

    if len(df) < TRAINING_CONFIG["min_labeled_samples"]:
        logger.warning(
            f"⏸️ {len(df)} labeled samples. Need {TRAINING_CONFIG['min_labeled_samples']}."
        )
        return None

    X = df[CATEGORICAL_FEATURES + NUMERIC_FEATURES]
    y = df[TRAINING_CONFIG["target_column"]]

    # ======================================================
    # 🔥 TRAIN / TEST SPLIT (IMPORTANT FIX)
    # ======================================================
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # ======================================================
    # PREPROCESSING PIPELINE
    # ======================================================
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
    ])

    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.05,
        eval_metric="logloss",
        random_state=42
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    # ======================================================
    # TRAIN
    # ======================================================
    pipeline.fit(X_train, y_train)

    # ======================================================
    # EVALUATE (ON TEST SET)
    # ======================================================
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test,
        y_pred,
        average="binary",
        zero_division=0
    )

    auc = roc_auc_score(y_test, y_prob) if len(y.unique()) > 1 else 0.5

    metrics = {
        "precision": round(float(prec), 3),
        "recall": round(float(rec), 3),
        "f1": round(float(f1), 3),
        "roc_auc": round(float(auc), 3),
        "samples": len(df),
        "trained_at": datetime.utcnow().isoformat()
    }

    # ======================================================
    # SAVE MODEL
    # ======================================================
    version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    model_path = str(MODELS_DIR / f"scorer_{version}.joblib")

    joblib.dump(pipeline, model_path)

    register_model(version, model_path, metrics)
    activate_model(version)

    logger.info(f"✅ Trained & activated {version} | Metrics: {metrics}")

    return {
        "version": version,
        "model_path": model_path,
        "metrics": metrics
    }


if __name__ == "__main__":
    run_training()