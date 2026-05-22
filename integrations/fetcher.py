from typing import List, Dict


class LeadFetcher:

    def __init__(self, client):
        self.client = client

    def fetch_leads(self) -> List[Dict]:

        print("📡 Fetching leads automatically...")

        endpoint = "/lead/table"

        payload = {
            "page": 1,
            "quantity": 50000,
            "sortField": "sf_created_at",
            "isAscending": False,
            "searchString": "",
            "filters": [],
            "isOr": True,
        }

        try:

            # =========================================
            # CRM API REQUEST
            # =========================================

            response = self.client.put(
                endpoint=endpoint,
                payload=payload
            )

            print("✅ CRM response received")

            # =========================================
            # RESPONSE DEBUG
            # =========================================

            print("📄 RESPONSE:")
            print(str(response)[:2000])

            # =========================================
            # HANDLE RESPONSE TYPES
            # =========================================

            if isinstance(response, dict):

                data = response

            else:

                try:
                    data = response.json()

                except Exception:

                    print("❌ Failed parsing JSON")

                    return []

            # =========================================
            # API SUCCESS CHECK
            # =========================================

            if not data.get("success", False):

                print("❌ API ERROR:")
                print(data)

                return []

            # =========================================
            # EXTRACT LEADS
            # =========================================

            leads = (
                data.get("data", {})
                .get("entities", [])
            )

            print(f"✅ TOTAL LEADS FETCHED: {len(leads)}")

            return leads

        except Exception as e:

            print(f"❌ Failed fetching leads: {e}")

            return []