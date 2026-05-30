import pandas as pd
from ml_pipeline.config import NUMERIC_FEATURES, CATEGORICAL_FEATURES


def prepare_features(raw_lead: dict) -> pd.DataFrame:
    df = pd.DataFrame([raw_lead])

    for col in NUMERIC_FEATURES:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    for col in CATEGORICAL_FEATURES:
        if col not in df.columns:
            df[col] = "unknown"
        df[col] = df[col].astype(str).str.strip().replace("", "unknown")

    if "lead_age_bucket" not in df.columns:
        df["lead_age_bucket"] = pd.cut(
            df["days_since_first_contact"],
            bins=[-1, 3, 7, 14, 30, 999],
            labels=["0-3", "4-7", "8-14", "15-30", "30+"],
        ).astype(str)

    if "budget_per_size" not in df.columns:
        df["budget_per_size"] = (
            df["estimated_budget"] / (df["company_size"] + 1)
        )

    return df
