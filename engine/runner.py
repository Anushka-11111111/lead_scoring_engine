from adapters.signal_cleaner import SignalCleaner
from core_contracts.feature_quality import FeatureQualityLayer
from scoring.fusion_layer import FusionLayer
from scoring.ml_refinement import MLRefinementLayer

from adapters.field_extractor import FieldExtractor
from intelligence.signal_builder import SignalBuilder
from rules_engine.rule_parser import RuleParser
from rules_engine.rule_executor import RuleExecutor

from services.analytics_service import (
    SCRAPED_LEADS,
    SCRAPE_STATUS
)


def run(leads, pusher=None):

    print("🧠 AI ENGINE STARTED")

    # =========================
    # RESET DASHBOARD STATE
    # =========================
    SCRAPED_LEADS.clear()

    SCRAPE_STATUS["running"] = True
    SCRAPE_STATUS["completed"] = False
    SCRAPE_STATUS["processed"] = 0
    SCRAPE_STATUS["total"] = len(leads)

    # =========================
    # PIPELINE INIT
    # =========================
    extractor = FieldExtractor()
    cleaner = SignalCleaner()
    quality_layer = FeatureQualityLayer()
    signal_builder = SignalBuilder()
    fusion = FusionLayer()
    ml_refiner = MLRefinementLayer()

    rules = RuleParser().load_rules("rules.json")

    executor = RuleExecutor()

    processed = 0

    # =========================
    # PROCESS LEADS
    # =========================
    for lead in leads:

        lead_id = str(
            lead.get("id")
            or lead.get("_id")
            or lead.get("sf_id")
            or "unknown"
        )

        try:

            # =========================
            # EXTRACT / SCORE
            # =========================
            observations = extractor.extract_all_fields(lead)

            observations = cleaner.clean(observations)

            quality = quality_layer.compute(observations)

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

            rule_score = result.get("final_score", 0)

            label = result.get(
                "classification",
                "Cold Lead"
            )

            breakdown = result.get(
                "breakdown",
                ""
            )

            ml_out = ml_refiner.refine(
                observations,
                rule_score,
                debug=True
            )

            ml_prob = round(
                ml_out["ml_probability"] * 100,
                1
            )

            # =========================
            # COMPANY NAME FIX
            # =========================
            company_name = (
                lead.get("sf_company_name")
                or lead.get("company_name")
                or lead.get("company")
                or lead.get("sf_company")
                or "Unknown Company"
            )

            # =========================
            # LEAD NAME FIX
            # =========================
            lead_name = (
                lead.get("sf_first_name")
                or lead.get("name")
                or lead.get("full_name")
                or lead.get("sf_name")
                or "Unknown Lead"
            )

            # =========================
            # PAYLOAD
            # =========================
            payload = {
                "ai_lead_score_test": rule_score,
                "ai_label_test": label,
                "ai_confidence_test": int(rule_score),
                "ai_explanation_test": breakdown,
                "ml_conversion_probability": ml_prob,
                "ml_confidence_level": "Low"
            }

            # =========================
            # PUSH TO CRM
            # =========================
            if pusher:

                try:
                    pusher.push_score(
                        lead_id,
                        payload
                    )

                except Exception as e:
                    print(
                        f"⚠️ Push failed for {lead_id}: {e}"
                    )

            # =========================
            # PUSH TO DASHBOARD
            # =========================
            SCRAPED_LEADS.append({

                "lead_id": lead_id,

                "name": lead_name,

                "company": company_name,

                "score": rule_score,

                "label": label,

                "ml_probability": ml_prob
            })

            processed += 1

            SCRAPE_STATUS["processed"] = processed

            print(
                f"✅ {lead_name} | "
                f"{company_name} | "
                f"Score: {rule_score}"
            )

        except Exception as e:

            print(
                f"❌ Lead failed {lead_id}: {e}"
            )

    # =========================
    # FINAL STATUS
    # =========================
    SCRAPE_STATUS["running"] = False
    SCRAPE_STATUS["completed"] = True

    print(f"🔥 TOTAL PROCESSED: {processed}")

    return processed