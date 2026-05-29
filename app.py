from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.sync import router as sync_router
from api.routes.analytics import router as analytics_router
from api.routes.score import router as score_router
from api.routes.leads import router as leads_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(sync_router)
app.include_router(analytics_router)
app.include_router(score_router)
app.include_router(leads_router)


@app.get("/")
def root():
    return {
        "message": "AI CRM Backend Running"
    }