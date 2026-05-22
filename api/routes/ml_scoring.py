from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime
from scoring.ml_scorer import calculate_ml_score
from services.ml_feedback import record_outcome
from ml_pipeline.model_registry import get_active_model, list_models
from ml_pipeline.config import LEADS_FILE

router = APIRouter()

class LeadPayload(BaseModel):
    lead_id: int
    industry: Optional[str] = None
    lead_source: Optional[str] = None
    company_size: Optional[float] = None
    estimated_budget: Optional[float] = None
    created_at: Optional[str] = None
    days_since_first_contact: Optional[int] = 0

class OutcomePayload(BaseModel):
    lead_id: int
    contacted: bool = False
    replied: bool = False
    meeting_booked: bool = False
    converted: bool = False  # 1 = won, 0 = not won
    lost: bool = False       # 1 = lost, 0 = not lost
    revenue: Optional[float] = None

@router.post("/lead", status_code=201)
def store_lead(payload: LeadPayload):
    """Store a new lead for future feedback tracking"""
    lead = payload.model_dump()
    lead["created_at"] = lead["created_at"] or datetime.utcnow().isoformat()
    
    new_row = pd.DataFrame([lead])
    if LEADS_FILE.exists():
        new_row.to_csv(LEADS_FILE, mode="a", header=False, index=False)
    else:
        new_row.to_csv(LEADS_FILE, index=False)
    
    return {"status": "lead_stored", "lead_id": payload.lead_id}

@router.post("/predict")
def predict_score(payload: LeadPayload):
    """Score a lead using the active ML model (independent of rules)"""
    store_lead(payload)  # Track for feedback loop
    
    score = calculate_ml_score(payload.model_dump())
    active = get_active_model()
    
    return {
        "lead_id": payload.lead_id,
        "score": score,
        "model_version": active["version"] if active else "none",
        "independence_note": "ML score uses ONLY raw attributes — no rule_score injection"
    }

@router.post("/outcome")
def update_outcome(payload: OutcomePayload):
    """Record final outcome for continuous learning"""
    success = record_outcome(payload.model_dump())
    if not success:
        raise HTTPException(status_code=400, detail="Failed to record outcome")
    return {"status": "outcome_recorded", "lead_id": payload.lead_id}

@router.get("/model/status")
def model_status():
    """Get active model info and metrics"""
    active = get_active_model()
    if not active:
        return {"status": "no_active_model", "message": "Run training first"}
    
    return {
        "version": active["version"],
        "metrics": active["metrics"],
        "activated_at": active["created_at"],
        "model_path": active["path"]
    }

@router.get("/model/list")
def list_all_models():
    """List all registered model versions"""
    return {"models": list_models()}