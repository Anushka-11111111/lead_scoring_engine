from fastapi import APIRouter
from pydantic import BaseModel, Field
from threading import Thread

from services.scraping_service import ScrapingService

router = APIRouter()


class SyncRequest(BaseModel):
    quantity: int = Field(default=50, ge=1, le=1000)


@router.post("/start-sync")
def start_sync(body: SyncRequest = SyncRequest()):

    service = ScrapingService()

    thread = Thread(
        target=service.start,
        kwargs={"quantity": body.quantity},
    )

    thread.start()

    return {
        "message": "Sync started",
        "quantity": body.quantity,
    }
