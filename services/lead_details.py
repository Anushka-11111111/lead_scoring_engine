from typing import Any, Dict, List


def _display_value(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, dict):
        return str(value.get("label") or value.get("name") or value.get("value") or value)
    if isinstance(value, list):
        if not value:
            return "—"
        return ", ".join(_display_value(item) for item in value[:5])
    return str(value)


def format_crm_details(lead: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build readable label/value rows for the lead detail UI."""
    priority_keys = [
        ("sf_id", "Lead ID"),
        ("_id", "CRM Record ID"),
        ("sf_first_name", "First Name"),
        ("sf_last_name", "Last Name"),
        ("name", "Name"),
        ("sf_email", "Email"),
        ("email", "Email"),
        ("sf_phone", "Phone"),
        ("phone", "Phone"),
        ("sf_company_name", "Company"),
        ("company", "Company"),
        ("sf_source", "Source"),
        ("sf_industry", "Industry"),
        ("industry", "Industry"),
        ("sf_created_at", "Created At"),
        ("sf_updated_at", "Updated At"),
        ("sf_owner", "Owner"),
        ("sf_latest_activity_on", "Latest Activity"),
    ]

    rows: List[Dict[str, str]] = []
    seen = set()

    for key, label in priority_keys:
        if key in lead and key not in seen:
            seen.add(key)
            rows.append({"label": label, "value": _display_value(lead[key])})

    for key, value in sorted(lead.items()):
        if key in seen or (key.startswith("_") and key != "_id"):
            continue
        if isinstance(value, (dict, list)) and key not in ("sf_source", "sf_owner"):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            seen.add(key)
            rows.append({
                "label": key.replace("sf_", "").replace("_", " ").title(),
                "value": _display_value(value),
            })

    return rows
