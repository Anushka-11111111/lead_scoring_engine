# integrations/transformers.py

def normalize_lead(raw):

    return {
        "lead_id": raw.get("id"),

        "name": raw.get("name"),

        "email": raw.get("email"),

        "phone": raw.get("phone"),

        "company": raw.get("company"),

        "industry": raw.get("industry"),

        "employee_count": raw.get("employees"),

        "annual_revenue": raw.get("revenue"),

        "source": raw.get("source"),

        "website": raw.get("website"),

        "linkedin": raw.get("linkedin"),

        "country": raw.get("country"),

        "created_at": raw.get("createdAt")
    }