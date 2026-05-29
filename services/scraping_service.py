from integrations.crm_client import CRMClient
from integrations.pusher import ScorePusher
from integrations.fetcher import LeadFetcher

from engine.runner import run


class ScrapingService:

    def start(self, quantity: int | None = None):

        print("🚀 API Sync Service Started")

        client = CRMClient.from_settings()

        pusher = ScorePusher(client)

        fetcher = LeadFetcher(client)

        leads = fetcher.fetch_leads(quantity=quantity)

        print(f"📦 Leads fetched: {len(leads)}")

        run(
            leads=leads,
            pusher=pusher
        )

        print("✅ Sync completed successfully")
