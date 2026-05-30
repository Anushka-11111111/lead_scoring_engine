from fastapi import APIRouter
from pydantic import BaseModel, Field
from threading import Thread

from api.routes.config import require_crm_client
from services.scraping_service import ScrapingService

router = APIRouter()


class SyncRequest(BaseModel):
    quantity: int = Field(default=50, ge=1, le=1000)


@router.post("/start-sync")
def start_sync(body: SyncRequest = SyncRequest()):
    require_crm_client()

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
