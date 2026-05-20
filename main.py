from adapters.signal_cleaner import SignalCleaner
from core_contracts.feature_quality import FeatureQualityLayer
from scoring.fusion_layer import FusionLayer
from scoring.ml_refinement import MLRefinementLayer

from integrations.fetcher import LeadFetcher

from adapters.field_extractor import FieldExtractor
from intelligence.signal_builder import SignalBuilder
from rules_engine.rule_parser import RuleParser
from rules_engine.rule_executor import RuleExecutor


def format_crm_output(rule_score: float, label: str, breakdown: str, ml_prob: float):

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

            readable = RULE_TEXT_MAP.get(rule_name, rule_name)

            rule_lines.append(f"- {readable} ({score_part})")

    rule_text = "\n".join(rule_lines) if rule_lines else "- No rule triggers matched."

    ml_level = "High" if ml_prob >= 70 else "Moderate" if ml_prob >= 40 else "Low"

    ml_insight = (
        f"- Conversion Probability: {ml_prob:.1f}% ({ml_level})\n"
        f"- ML Confidence: Low (hybrid refinement phase)\n"
        f"- Note: ML signal is currently limited due to lack of behavioral data."
    )

    summary = (
        "Rule engine strongly qualifies this lead as high priority."
        if rule_score >= 70 else
        "Rule engine flags this lead as moderately qualified."
        if rule_score >= 50 else
        "Rule engine indicates lower priority."
    )

    return (
        f"{rule_score} – {label}.\n\n"
        f"Rule-Based Explanation:\n{rule_text}\n\n"
        f"📊 ML Insight:\n{ml_insight}\n\n"
        f"🧠 Summary:\n{summary}"
    )


# ✅ CLEAN ENGINE (NO PLAYWRIGHT HERE)
def run(context):

    print("🧠 AI Lead Scoring Engine Started")

    # =========================
    # FETCH LEADS USING SHARED CONTEXT
    # =========================

    fetcher = LeadFetcher(context)

    leads = fetcher.fetch_leads()

    print(f"📦 TOTAL LEADS FETCHED: {len(leads)}")

    if not leads:
        print("⚠️ No leads fetched")
        return

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

    for lead in leads:

        lead_id = str(
            lead.get("id")
            or lead.get("sf_id")
            or lead.get("_id")
            or "unknown"
        )

        print(f"\n🚀 PROCESSING LEAD: {lead_id}")

        try:

            observations = extractor.extract_all_fields(lead)
            observations = cleaner.clean(observations)
            quality = quality_layer.compute(observations)
            signals = signal_builder.build(observations, quality)
            triggers = executor.debug_execute(signals, rules)
            result = fusion.compute(triggers, quality)

            rule_score = result.get("final_score", 0)
            label = result.get("classification", "🔵 Cold Lead")
            breakdown = result.get("breakdown", "")

            ml_out = ml_refiner.refine(
                observations,
                rule_score,
                debug=True
            )

            ml_prob = round(ml_out["ml_probability"] * 100, 1)

            crm_output = format_crm_output(
                rule_score,
                label,
                breakdown,
                ml_prob
            )

            payload = {
                "ai_lead_score_test": rule_score,
                "ai_label_test": label.replace("🔥 ", "").replace("🟡 ", "").replace("🔵 ", ""),
                "ai_confidence_test": int(rule_score),
                "ai_explanation_test": crm_output,
                "ml_conversion_probability": ml_prob,
                "ml_confidence_level": "Low"
            }

            print("\n📤 FINAL PAYLOAD:")
            print(payload)

            processed += 1

        except Exception as e:
            print(f"❌ Failed lead {lead_id}: {e}")

    print(f"\n🔥 TOTAL PROCESSED: {processed}")

from dotenv import load_dotenv
load_dotenv()