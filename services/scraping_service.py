import os

from dotenv import load_dotenv

load_dotenv(override=True)

from integrations.auth import CRMAuth
from integrations.crm_client import CRMClient
from integrations.pusher import ScorePusher
from integrations.fetcher import LeadFetcher

from engine.runner import run


class ScrapingService:

    def start(self):

        print("🚀 API Sync Service Started")

        # =========================================
        # CRM AUTH
        # =========================================

        auth = CRMAuth()

        # =========================================
        # BASE URL
        # =========================================

        base_url = os.getenv("CRM_BASE_URL")

        if not base_url:

            raise ValueError(
                "❌ CRM_BASE_URL missing in .env"
            )

        # =========================================
        # CRM CLIENT
        # =========================================

        client = CRMClient(
            base_url=base_url,
            auth=auth
        )

        # =========================================
        # PUSHER
        # =========================================

        pusher = ScorePusher(client)

        # =========================================
        # FETCH LEADS
        # =========================================

        fetcher = LeadFetcher(client)

        leads = fetcher.fetch_leads()

        print(f"📦 Leads fetched: {len(leads)}")

        # =========================================
        # RUN ENGINE
        # =========================================

        run(
            leads=leads,
            pusher=pusher
        )

        print("✅ Sync completed successfully")