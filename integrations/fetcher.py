from typing import List, Dict
from playwright.sync_api import sync_playwright
import time


class LeadFetcher:
    """
    Fetches lead data directly from the Togile CRM platform
    using Playwright browser automation.
    """

    def __init__(self, client=None):
        self.client = client

    def fetch_leads(self) -> List[Dict]:

        TOGILE_APP_URL = "https://app.togile.com"
        API_URL = "https://server.togile.com/lead/table"

        all_leads = []

        with sync_playwright() as p:

            # ✅ FIXED FOR WINDOWS
            # Removed invalid Linux executable_path
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )

            context = browser.new_context()
            page = context.new_page()

            print("🌐 Opening Togile...")
            page.goto(TOGILE_APP_URL)

            input("🔐 Login manually, then press ENTER...")

            page.wait_for_load_state("networkidle")
            time.sleep(3)

            print("📡 Fetching leads...")

            # ==================================================
            # FETCH ONLY FIRST 5 LEADS
            # ==================================================
            payload = {
                "page": 1,
                "quantity": 5,
                "sortField": "sf_created_at",
                "isAscending": False,
                "searchString": "",
                "filters": [],
                "isOr": True
            }

            response = context.request.put(
                API_URL,
                data=payload
            )

            try:
                data = response.json()

            except Exception:

                print("❌ Failed to parse response")
                print(response.text())

                browser.close()

                return []

            browser.close()

        print("🔍 RAW RESPONSE:", data)

        if not data.get("success", False):

            print("❌ API error:", data)

            return []

        leads = data.get("data", {}).get("entities", [])

        print(f"✅ TOTAL LEADS FETCHED: {len(leads)}")

        return leads