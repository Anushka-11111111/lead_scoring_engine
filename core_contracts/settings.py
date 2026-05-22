from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # ✅ Required CRM credentials
    CRM_BASE_URL: str
    CRM_API_KEY: str
    CRM_SECRET_KEY: str
    
    # ✅ Optional CRM fields
    CRM_REDIRECT_LOGIN_URL: Optional[str] = None
    CRM_EMAIL: Optional[str] = None
    CRM_PASSWORD: Optional[str] = None
    TOGILE_TOKEN: Optional[str] = None
    
    # ✅ ML Config (with defaults)
    ML_RETRAIN_INTERVAL_HOURS: int = 12
    ML_MIN_LABELED_SAMPLES: int = 50

    # ✅ Ignore any extra env vars (like cookies, analytics, etc.)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # ← This prevents ValidationError on unknown vars
    )

settings = Settings()

# 🔒 Safety check on startup for required fields only
for field in ["CRM_BASE_URL", "CRM_API_KEY", "CRM_SECRET_KEY"]:
    if not getattr(settings, field):
        raise RuntimeError(f"❌ Missing required env variable: {field}")