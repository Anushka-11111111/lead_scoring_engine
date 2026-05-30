# Central registry of CRM fields that participate in rule scoring.
# Multiple aliases cover Togile (sf_*) and generic CRM payloads.

def _entry(signal_type: str, category: str, weight: int) -> dict:
    return {
        "signal_type": signal_type,
        "category": category,
        "weight": weight,
    }


_EMAIL = _entry("email_signal", "identity", 10)
_PHONE = _entry("phone_signal", "identity", 10)
_NAME = _entry("identity_signal", "identity", 6)
_COMPANY = _entry("company_signal", "identity", 8)
_CREATED = _entry("lead_recency_signal", "temporal", 15)
_ACTIVITY = _entry("activity_recency_signal", "temporal", 20)
_PIPELINE = _entry("conversion_probability_signal", "intent", 25)
_SOURCE = _entry("acquisition_channel_signal", "marketing", 10)
_LOCATION = _entry("location_signal", "demographic", 5)

FIELD_MAPPING = {
    # Email
    "sf_email": _EMAIL,
    "email": _EMAIL,
    # Phone
    "sf_phone_number.value": _PHONE,
    "sf_phone": _PHONE,
    "phone": _PHONE,
    # Name
    "sf_first_name": _NAME,
    "sf_name": _NAME,
    "name": _NAME,
    "first_name": _NAME,
    # Company
    "sf_company_name": _COMPANY,
    "sf_company": _COMPANY,
    "company": _COMPANY,
    "company.name": _COMPANY,
    # Created / activity
    "sf_created_at": _CREATED,
    "created_at": _CREATED,
    "createdat": _CREATED,
    "sf_latest_activity_on": _ACTIVITY,
    "sf_latest_activity_day_at": _ACTIVITY,
    "latest_activity_on": _ACTIVITY,
    # Pipeline
    "sf_pipeline_stage.winprobability": _PIPELINE,
    "pipeline_stage.winprobability": _PIPELINE,
    "winprobability": _PIPELINE,
    # Source
    "sf_source.label": _SOURCE,
    "sf_source.value": _SOURCE,
    "cf_lead_source.label": _SOURCE,
    "source": _SOURCE,
    "lead_source": _SOURCE,
    # Location
    "sf_city": _LOCATION,
    "sf_state": _LOCATION,
    "sf_country": _LOCATION,
    "city": _LOCATION,
    "state": _LOCATION,
    "country": _LOCATION,
}
