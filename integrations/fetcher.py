from typing import List, Dict


class LeadFetcher:

    def __init__(self, client):
        self.client = client

    def fetch_leads(self) -> List[Dict]:

        print("📡 Fetching leads automatically...")

        endpoint = "/lead/table"

        payload = {
            "page": 1,
            "quantity": 1650,
            "sortField": "sf_created_at",
            "isAscending": False,
            "searchString": "",
            "filters": [],
            "isOr": True,
        }

        try:

            # CRMClient already returns parsed JSON
            data = self.client.put(
                endpoint=endpoint,
                payload=payload
            )

            print("📄 RESPONSE RECEIVED")

        except Exception as e:

            print(f"❌ Failed fetching leads: {e}")

            return []

        # =========================
        # API SUCCESS CHECK
        # =========================

        if not data.get("success"):

            print("❌ API ERROR:")
            print(data)

            return []

        # =========================
        # EXTRACT LEADS
        # =========================

        leads = data.get("data", {}).get("entities", [])

        print(f"✅ TOTAL LEADS FETCHED: {len(leads)}")

        return leads