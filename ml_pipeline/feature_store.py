import pandas as pd
from ml_pipeline.config import NUMERIC_FEATURES, CATEGORICAL_FEATURES


def prepare_features(raw_lead: dict) -> pd.DataFrame:
    df = pd.DataFrame([raw_lead])

    # --------------------------------------------------
    # BASIC NUMERIC FEATURES
    # --------------------------------------------------
    for col in NUMERIC_FEATURES:
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0.0)

    # --------------------------------------------------
    # CATEGORICAL FEATURES
    # --------------------------------------------------
    for col in CATEGORICAL_FEATURES:
        df[col] = str(df.get(col, "unknown")).strip() or "unknown"

    # --------------------------------------------------
    # 🔥 ADD DERIVED FEATURES (THIS IS KEY FIX)
    # --------------------------------------------------

    # Lead age bucket
    df["lead_age_bucket"] = pd.cut(
        df["days_since_first_contact"],
        bins=[-1, 3, 7, 14, 30, 999],
        labels=["0-3", "4-7", "8-14", "15-30", "30+"]
    ).astype(str)

    # Budget intensity
    df["budget_per_size"] = (
        df["estimated_budget"] / (df["company_size"] + 1)
    )

    return df