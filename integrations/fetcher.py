from typing import List, Dict
from playwright.sync_api import sync_playwright
import time


class LeadFetcher:
    """
    Fetches lead data directly from the Togile CRM platform
    using Playwright browser automation.

    Why Playwright?
    Some CRM systems:
    - Use session-based authentication
    - Require browser login flows
    - Block direct API requests without valid browser context

    Playwright solves this by:
    - Launching a real browser session
    - Allowing manual login
    - Reusing authenticated browser context
    - Making authenticated API calls internally

    Main Responsibilities:
    - Open CRM frontend
    - Allow manual authentication
    - Reuse active session
    - Fetch lead data from backend API
    """

    def __init__(self, client=None):
        """
        Initializes lead fetcher.

        Args:
            client:
                Optional API client (currently unused).
                Reserved for future extensibility.
        """

        # Not required for Playwright flow right now
        self.client = client

    def fetch_leads(self) -> List[Dict]:
        """
        Fetches ALL leads from Togile CRM using pagination.

        Flow:
        1. Launch browser
        2. Open Togile app
        3. User logs in manually
        4. Reuse authenticated browser session
        5. Loop through all API pages
        6. Aggregate all lead entities
        7. Return complete lead dataset

        Returns:
            List[Dict]:
                List of ALL CRM lead records.
        """

        # --------------------------------------------------
        # Frontend application URL
        # --------------------------------------------------
        TOGILE_APP_URL = "https://app.togile.com"

        # --------------------------------------------------
        # Backend API endpoint
        # --------------------------------------------------
        API_URL = "https://server.togile.com/lead/table"

        # --------------------------------------------------
        # Store all fetched leads
        # --------------------------------------------------
        all_leads = []

        # --------------------------------------------------
        # Start Playwright browser automation
        # --------------------------------------------------
        with sync_playwright() as p:

            # Launch browser
            browser = p.chromium.launch(headless=False)

            # Create browser session
            context = browser.new_context()

            # Create browser tab
            page = context.new_page()

            # --------------------------------------------------
            # Open Togile frontend
            # --------------------------------------------------
            print("🌐 Opening Togile...")

            page.goto(TOGILE_APP_URL)

            # --------------------------------------------------
            # Manual login
            # --------------------------------------------------
            input("🔐 Login manually, then press ENTER...")

            page.wait_for_load_state("networkidle")

            # Extra safety delay
            time.sleep(3)

            # --------------------------------------------------
            # Pagination setup
            # --------------------------------------------------
            current_page = 1
            quantity = 50

            # --------------------------------------------------
            # Track duplicate leads
            # --------------------------------------------------
            seen_ids = set()

            # --------------------------------------------------
            # Fetch all pages
            # --------------------------------------------------
            while True:

                print(f"\n📡 Fetching page {current_page}...")

                payload = {

                    # Dynamic page number
                    "page": current_page,

                    # Leads per page
                    "quantity": quantity,

                    # Sort field
                    "sortField": "sf_created_at",

                    # Latest first
                    "isAscending": False,

                    # Search keyword
                    "searchString": "",

                    # CRM filters
                    "filters": [],

                    # OR filtering logic
                    "isOr": True
                }

                # --------------------------------------------------
                # Authenticated API request
                # --------------------------------------------------
                response = context.request.put(
                    API_URL,
                    data=payload
                )

                # --------------------------------------------------
                # Attempt JSON parsing
                # --------------------------------------------------
                try:
                    data = response.json()

                except Exception:

                    print("❌ Failed to parse response")

                    print(response.text())

                    break

                # --------------------------------------------------
                # API success validation
                # --------------------------------------------------
                if not data.get("success", False):

                    print("❌ API error:", data)

                    break

                # --------------------------------------------------
                # Extract leads from response
                # --------------------------------------------------
                leads = data.get("data", {}).get("entities", [])

                print(f"✅ Leads fetched: {len(leads)}")

                # --------------------------------------------------
                # Stop if no leads
                # --------------------------------------------------
                if not leads:

                    print("🏁 No more leads found.")

                    break

                # --------------------------------------------------
                # Detect duplicate pages
                # --------------------------------------------------
                new_leads = []

                for lead in leads:

                    lead_id = str(
                        lead.get("id")
                        or lead.get("sf_id")
                        or lead.get("_id")
                        or ""
                    )

                    # Skip duplicate leads
                    if lead_id not in seen_ids:

                        seen_ids.add(lead_id)

                        new_leads.append(lead)

                # --------------------------------------------------
                # Stop if page is fully duplicate
                # --------------------------------------------------
                if not new_leads:

                    print("🏁 Duplicate page detected. Stopping pagination.")

                    break

                # --------------------------------------------------
                # Store new leads
                # --------------------------------------------------
                all_leads.extend(new_leads)

                print(f"📦 Total unique leads: {len(all_leads)}")

                # --------------------------------------------------
                # Last page detection
                # --------------------------------------------------
                if len(leads) < quantity:

                    print("🏁 Final partial page reached.")

                    break

                # --------------------------------------------------
                # Next page
                # --------------------------------------------------
                current_page += 1

                # Small safety delay
                time.sleep(1)

            # --------------------------------------------------
            # Close browser
            # --------------------------------------------------
            browser.close()

        # --------------------------------------------------
        # Final stats
        # --------------------------------------------------
        print(f"\n🔥 TOTAL UNIQUE LEADS FETCHED: {len(all_leads)}")

        # --------------------------------------------------
        # Return all leads
        # --------------------------------------------------
        return all_leads