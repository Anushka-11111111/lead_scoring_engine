from fastapi import APIRouter
from threading import Thread

from services.scraping_service import ScrapingService

router = APIRouter()


@router.post("/start-sync")
def start_sync():

    service = ScrapingService()

    thread = Thread(
        target=service.start
    )

    thread.start()

    return {
        "message": "https://app.togile.com"
    }