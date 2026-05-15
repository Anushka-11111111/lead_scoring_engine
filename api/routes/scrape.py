from fastapi import APIRouter
import threading

from services.scraping_service import ScrapingService
from state.runtime_store import SCRAPE_STATUS

router = APIRouter()

scraper = ScrapingService()


@router.post("/start-scraping")
def start_scraping():

    if SCRAPE_STATUS["running"]:

        return {
            "message": "Scraping already running"
        }

    thread = threading.Thread(
        target=scraper.run_pipeline
    )

    thread.start()

    return {
        "message": "Scraping started"
    }