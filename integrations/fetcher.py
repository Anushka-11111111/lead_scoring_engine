from typing import List, Dict

from core_contracts.settings import settings


class LeadFetcher:

    def __init__(self, client):
        self.client = client

    def fetch_leads(self, quantity: int | None = None) -> List[Dict]:

        qty = quantity if quantity is not None else settings.CRM_LEADS_QUANTITY
        print(f"Fetching leads automatically (quantity={qty})...")

        try:
            response = self.client.fetch_leads_table(
                page=1,
                quantity=qty,
                sort_field="sf_created_at",
                is_ascending=False,
            )

            if not isinstance(response, dict) or not response.get("success", False):
                print("API ERROR:")
                print(response)
                return []

            leads = (response.get("data", {}) or {}).get("entities", []) or []

            print(f"TOTAL LEADS FETCHED: {len(leads)}")

            return leads

        except Exception as e:

            print(f"Failed fetching leads: {e}")

            return []
