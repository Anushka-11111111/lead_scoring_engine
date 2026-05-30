# =========================================
# =========================================
# LOAD ENV FIRST
# =========================================

from dotenv import load_dotenv
load_dotenv()

# =========================================
# IMPORTS
# =========================================

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler

# --- Existing Pipeline Imports ---

from integrations.fetcher import LeadFetcher

from adapters.field_extractor import FieldExtractor
from adapters.signal_cleaner import SignalCleaner

from core_contracts.feature_quality import FeatureQualityLayer

from scoring.fusion_layer import FusionLayer
from scoring.ml_refinement import MLRefinementLayer

from intelligence.signal_builder import SignalBuilder

from rules_engine.rule_parser import RuleParser
from rules_engine.rule_executor import RuleExecutor

# --- ML & Sync Imports ---

from api.routes import ml_scoring

from services.crm_ml_sync import sync_crm_outcomes_to_ml

from ml_pipeline.train_model import run_training

from scoring.ml_scorer import calculate_ml_score

# --- CRM IMPORTS ---

from integrations.crm_client import CRMClient

# =========================================
# LOGGING
# =========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# =========================================
# GLOBAL ANALYTICS STATE
# =========================================

analytics_state = {
    "running": False,
    "processed": 0,
    "total": 0,
    "current_lead": "None",
    "completed": False,
    "top_leads": []
}

# =========================================
# FORMAT CRM OUTPUT
# =========================================

def format_crm_output(
    rule_score: float,
    label: str,
    breakdown: str,
    ml_prob: float
):

    RULE_TEXT_MAP = {
        "Has Phone": "Phone number available",
        "Has Email": "Email address available",
        "Recent Lead": "Recently created lead",
        "High Pipeline Probability": "High deal probability",
        "Facebook Source": "Lead sourced from Facebook",
        "Missing Email": "Email not available",
        "Has Location Data": "Location information available",
    }

    rule_lines = []

    for item in breakdown.split(","):

        item = item.strip()

        if "(" in item:

            rule_name = item.split("(")[0].strip()

            score_part = item.split("(")[1].strip(")")

            readable = RULE_TEXT_MAP.get(
                rule_name,
                rule_name
            )

            rule_lines.append(
                f"- {readable} ({score_part})"
            )

    rule_text = (
        "\n".join(rule_lines)
        if rule_lines
        else "- No rule triggers matched."
    )

    ml_level = (
        "High"
        if ml_prob >= 70
        else "Moderate"
        if ml_prob >= 40
        else "Low"
    )

    ml_insight = (
        f"- Conversion Probability: {ml_prob:.1f}% ({ml_level})\n"
        f"- ML Confidence: {ml_level}\n"
        f"- Note: ML signal uses ONLY raw lead attributes."
    )

    summary = (
        "Rule engine strongly qualifies this lead as high priority."
        if rule_score >= 70
        else
        "Rule engine flags this lead as moderately qualified."
        if rule_score >= 50
        else
        "Rule engine indicates lower priority."
    )

    return (
        f"{rule_score} – {label}.\n\n"
        f"Rule-Based Explanation:\n{rule_text}\n\n"
        f"📊 ML Insight:\n{ml_insight}\n\n"
        f"🧠 Summary:\n{summary}"
    )

# =========================================
# MAIN PIPELINE
# =========================================

def run(context):

    logger.info("🧠 AI Lead Scoring Engine Started")

    client = CRMClient.from_settings()

    fetcher = LeadFetcher(client)

    leads = fetcher.fetch_leads()

    logger.info(
        f"📦 TOTAL LEADS FETCHED: {len(leads)}"
    )

    if not leads:

        logger.warning("⚠️ No leads fetched")

        return

    extractor = FieldExtractor()

    cleaner = SignalCleaner()

    quality_layer = FeatureQualityLayer()

    signal_builder = SignalBuilder()

    fusion = FusionLayer()

    ml_refiner = MLRefinementLayer()

    rules = RuleParser().load_rules("rules.json")

    executor = RuleExecutor()

    processed = 0

    for lead in leads:

        lead_id = str(
            lead.get("sf_id")
            or lead.get("lead_id")
            or lead.get("crm_id")
            or lead.get("id")
            or "unknown"
        )

        logger.info(
            f"\n🚀 PROCESSING LEAD: {lead_id}"
        )

        try:

            observations = extractor.extract_all_fields(
                lead
            )

            observations = cleaner.clean(
                observations
            )

            quality = quality_layer.compute(
                observations
            )

            signals = signal_builder.build(
                observations,
                quality
            )

            triggers = executor.debug_execute(
                signals,
                rules
            )

            result = fusion.compute(
                triggers,
                quality
            )

            rule_score = result.get(
                "final_score",
                0
            )

            label = result.get(
                "classification",
                "🔵 Cold Lead"
            )

            breakdown = result.get(
                "breakdown",
                ""
            )

            ml_prob = calculate_ml_score({

                "industry": observations.get(
                    "industry",
                    "unknown"
                ),

                "lead_source": observations.get(
                    "lead_source",
                    "unknown"
                ),

                "company_size": observations.get(
                    "company_size",
                    0
                ),

                "estimated_budget": observations.get(
                    "estimated_budget",
                    0
                ),

                "days_since_first_contact":
                    observations.get(
                        "days_since_first_contact",
                        0
                    )
            })

            crm_output = format_crm_output(
                rule_score,
                label,
                breakdown,
                ml_prob
            )

            payload = {

                "ai_lead_score_test":
                    rule_score,

                "ai_label_test":
                    label.replace("🔥 ", "")
                    .replace("🟡 ", "")
                    .replace("🔵 ", ""),

                "ai_confidence_test":
                    int(rule_score),

                "ai_explanation_test":
                    crm_output,

                "ml_conversion_probability":
                    ml_prob
            }

            logger.info(
                f"\n📤 FINAL PAYLOAD:\n{payload}"
            )

            processed += 1

        except Exception as e:

            logger.error(
                f"❌ Failed lead {lead_id}: {e}",
                exc_info=True
            )

    logger.info(
        f"\n🔥 TOTAL PROCESSED: {processed}"
    )

# =========================================
# FASTAPI LIFESPAN
# =========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_training,
        "interval",
        hours=12,
        id="ml_retrain",
        replace_existing=True
    )

    scheduler.add_job(
        sync_crm_outcomes_to_ml,
        "interval",
        hours=6,
        id="crm_sync",
        replace_existing=True
    )

    scheduler.start()

    logger.info(
        "📅 Background schedulers started"
    )

    yield

    scheduler.shutdown(wait=False)

    logger.info(
        "🛑 Background schedulers stopped"
    )

# =========================================
# FASTAPI APP
# =========================================

app = FastAPI(
    title="CRM AI Scoring Engine",
    lifespan=lifespan
)

# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ROUTERS
# =========================================

app.include_router(
    ml_scoring.router,
    prefix="/ml",
    tags=["ML"]
)

# =========================================
# ANALYTICS ENDPOINT
# =========================================

@app.get("/analytics")
def get_analytics():

    top_leads = analytics_state["top_leads"]

    hot = len([
        l for l in top_leads
        if l.get("score", 0) >= 80
    ])

    warm = len([
        l for l in top_leads
        if 50 <= l.get("score", 0) < 80
    ])

    cold = len([
        l for l in top_leads
        if l.get("score", 0) < 50
    ])

    avg = (
        round(
            sum(
                l.get("score", 0)
                for l in top_leads
            ) / len(top_leads),
            1
        )
        if top_leads
        else 0
    )

    return {

        "total_leads":
            len(top_leads),

        "hot_leads":
            hot,

        "warm_leads":
            warm,

        "cold_leads":
            cold,

        "average_score":
            avg,

        "top_leads":
            top_leads[-10:],

        "status": {

            "running":
                analytics_state["running"],

            "processed":
                analytics_state["processed"],

            "total":
                analytics_state["total"],

            "current_lead":
                analytics_state["current_lead"],

            "completed":
                analytics_state["completed"]
        }
    }

# =========================================
# START SYNC
# =========================================

@app.post("/start-sync")
def start_sync():

    analytics_state["running"] = True

    analytics_state["completed"] = False

    analytics_state["processed"] = 0

    analytics_state["current_lead"] = "Starting..."

    try:

        client = CRMClient.from_settings()

        fetcher = LeadFetcher(client)

        logger.info("📡 Fetching leads automatically...")

        leads = fetcher.fetch_leads()

        analytics_state["total"] = len(leads)

        extractor = FieldExtractor()

        cleaner = SignalCleaner()

        quality_layer = FeatureQualityLayer()

        signal_builder = SignalBuilder()

        fusion = FusionLayer()

        rules = RuleParser().load_rules(
            "rules.json"
        )

        executor = RuleExecutor()

        analytics_state["top_leads"] = []

        for idx, lead in enumerate(leads):

            try:

                observations = extractor.extract_all_fields(
                    lead
                )

                observations = cleaner.clean(
                    observations
                )

                quality = quality_layer.compute(
                    observations
                )

                signals = signal_builder.build(
                    observations,
                    quality
                )

                triggers = executor.debug_execute(
                    signals,
                    rules
                )

                result = fusion.compute(
                    triggers,
                    quality
                )

                score = result.get(
                    "final_score",
                    0
                )

                label = result.get(
                    "classification",
                    "Cold Lead"
                )

                ml_prob = calculate_ml_score({

                    "industry": observations.get(
                        "industry",
                        "unknown"
                    ),

                    "lead_source": observations.get(
                        "lead_source",
                        "unknown"
                    ),

                    "company_size": observations.get(
                        "company_size",
                        0
                    ),

                    "estimated_budget": observations.get(
                        "estimated_budget",
                        0
                    ),

                    "days_since_first_contact":
                        observations.get(
                            "days_since_first_contact",
                            0
                        )
                })

                analytics_state["processed"] = idx + 1

                analytics_state["current_lead"] = str(
                    lead.get("sf_id")
                    or lead.get("lead_id")
                    or lead.get("crm_id")
                    or lead.get("id")
                    or "unknown"
                )

                analytics_state["top_leads"].append({

                    "lead_id": str(
                        lead.get("sf_id")
                        or lead.get("lead_id")
                        or lead.get("crm_id")
                        or lead.get("id")
                        or "unknown"
                    ),

                    "name": lead.get(
                        "name",
                        "Unknown"
                    ),

                    "company": lead.get(
                        "company",
                        "Unknown Company"
                    ),

                    "score": round(score, 1),

                    "label": label,

                    "ml_probability": round(
                        ml_prob,
                        1
                    )
                })

                logger.info(
                    f"✅ Processed lead {idx + 1}/{len(leads)}"
                )

            except Exception as lead_error:

                logger.error(
                    f"❌ Failed processing lead: {lead_error}",
                    exc_info=True
                )

        analytics_state["running"] = False

        analytics_state["completed"] = True

        analytics_state["current_lead"] = "Completed"

        logger.info("🔥 Lead sync completed")

        return {
            "status": "success",
            "processed": analytics_state["processed"]
        }

    except Exception as e:

        analytics_state["running"] = False

        analytics_state["completed"] = False

        logger.error(
            f"❌ Sync failed: {e}",
            exc_info=True
        )

        return {
            "status": "error",
            "message": str(e)
        }

# =========================================
# ENGINE RUN ENDPOINT
# =========================================

from pydantic import BaseModel
from typing import Any, Dict

class PipelinePayload(BaseModel):
    context: Dict[str, Any] = {}

@app.post("/engine/run")
def trigger_pipeline(payload: PipelinePayload):

    run(payload.context)

    return {
        "status": "pipeline_executed"
    }

# =========================================
# HEALTH
# =========================================

@app.get("/health")
def health_check():

    from ml_pipeline.model_registry import (
        get_active_model
    )

    active = get_active_model()

    return {

        "status":
            "healthy",

        "ml_model_active":
            active is not None,

        "model_version":
            active["version"]
            if active
            else None
    }