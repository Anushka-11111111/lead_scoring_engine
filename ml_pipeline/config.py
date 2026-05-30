from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "ml_data"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

LEADS_FILE = DATA_DIR / "leads.csv"
OUTCOMES_FILE = DATA_DIR / "outcomes.csv"
TRAINING_STATE_FILE = DATA_DIR / "training_state.json"

NUMERIC_FEATURES = [
    "company_size",
    "estimated_budget",
    "days_since_first_contact",
    "budget_per_size",
]

CATEGORICAL_FEATURES = [
    "industry",
    "lead_source",
    "lead_age_bucket",
]

TRAINING_CONFIG = {
    "min_labeled_samples": 100,
    "min_mature_samples": 3000,
    "retrain_interval_hours": 12,
    "target_column": "converted",
}
