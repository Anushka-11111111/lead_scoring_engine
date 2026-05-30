from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # CRM credentials — optional in .env; can be set at runtime via the dashboard
    CRM_BASE_URL: str = ""
    CRM_API_KEY: str = ""
    CRM_SECRET_KEY: str = ""
    CRM_ORIGIN: str = ""
    CRM_LEADS_QUANTITY: int = 500

    # ML Config (with defaults)
    ML_RETRAIN_INTERVAL_HOURS: int = 12
    ML_MIN_LABELED_SAMPLES: int = 100
    ML_MATURE_SAMPLES: int = 3000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
