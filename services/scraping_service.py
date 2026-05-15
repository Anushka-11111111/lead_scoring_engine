import os
from dotenv import load_dotenv
load_dotenv(override=True)

from playwright.sync_api import sync_playwright

from integrations.auth import CRMAuth
from integrations.crm_client import CRMClient
from integrations.pusher import ScorePusher
from integrations.fetcher import LeadFetcher

from engine.runner import run   # ✅ FIXED IMPORT


class ScrapingService:

    def start(self):

        print("🚀 Scraping service started")

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            print("🌐 Opening Togile")
            page.goto("https://app.togile.com/", wait_until="networkidle")

            print("🔐 Please login...")

            while True:
                try:
                    page.wait_for_selector("text=Leads", timeout=5000)
                    print("✅ Login detected")
                    break
                except:
                    print("⏳ Waiting for login...")
                    page.wait_for_timeout(3000)

            page.goto("https://app.togile.com/leads", wait_until="networkidle")
            page.wait_for_timeout(8000)

            # ✅ FIX COOKIE HANDLING
            cookies = context.cookies()
            auth = CRMAuth(cookies=cookies)

            base_url = os.getenv("CRM_BASE_URL")
            if not base_url:
                raise ValueError("CRM_BASE_URL missing in .env")

            client = CRMClient(base_url=base_url, auth=auth)
            pusher = ScorePusher(client)

            # ✅ FETCH LEADS
            fetcher = LeadFetcher(client)
            leads = fetcher.fetch_leads()

            print(f"📦 Leads fetched: {len(leads)}")

            # ✅ RUN ENGINE (NO context passed)
            run(leads=leads, pusher=pusher)

            print("🛑 Keeping browser open for inspection...")
            page.wait_for_timeout(15000)

            browser.close()