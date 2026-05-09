import os
from dotenv import load_dotenv

from adapters.signal_cleaner import SignalCleaner
from core_contracts.feature_quality import FeatureQualityLayer
from scoring.fusion_layer import FusionLayer
from scoring.ml_refinement import MLRefinementLayer  # 🆕 ADDED

# --- CRM LAYER ---
from integrations.auth import CRMAuth
from integrations.crm_client import CRMClient
from integrations.fetcher import LeadFetcher
from integrations.pusher import ScorePusher

# --- ENGINE LAYER ---
from adapters.field_extractor import FieldExtractor
from intelligence.signal_builder import SignalBuilder
from rules_engine.rule_parser import RuleParser
from rules_engine.rule_executor import RuleExecutor


# --- LOAD ENV ---
load_dotenv()


def format_crm_output(rule_score: float, label: str, breakdown: str, ml_prob: float) -> str:
    """
    Generates the exact polished CRM output format requested.
    Clearly separates Rule logic from ML insights.
    """
    RULE_TEXT_MAP = {
        "Has Phone": "Phone number available",
        "Has Email": "Email address available",
        "Recent Lead": "Recently created lead",
        "High Pipeline Probability": "High deal probability",
        "Facebook Source": "Lead sourced from Facebook",
        "Missing Email": "Email not available",
        "Has Location Data": "Location information available",
    }

    # 1️⃣ Rule-Based Explanation
    rule_lines = []
    for item in breakdown.split(","):
        item = item.strip()
        if "(" in item:
            rule_name = item.split("(")[0].strip()
            score_part = item.split("(")[1].strip(")")
            readable = RULE_TEXT_MAP.get(rule_name, rule_name)
            rule_lines.append(f"- {readable} ({score_part})")
    rule_text = "\n".join(rule_lines) if rule_lines else "- No rule triggers matched."

    # 2️⃣ ML Insight & Interpretation
    if ml_prob >= 70:
        ml_level = "High"
    elif ml_prob >= 40:
        ml_level = "Moderate"
    else:
        ml_level = "Low"

    ml_insight = (
        f"- Conversion Probability: {ml_prob:.1f}% ({ml_level})\n"
        f"- ML Confidence: Low (hybrid refinement phase)\n"
        f"- Note: ML signal is currently limited due to lack of behavioral data and may improve with richer inputs."
    )

    # 3️⃣ Reconciliation Summary
    if rule_score >= 70:
        summary = "Rule engine strongly qualifies this lead as high priority, while ML provides a neutral probability estimate."
    elif rule_score >= 50:
        summary = "Rule engine flags this lead as moderately qualified. ML suggests a consistent conversion likelihood."
    else:
        summary = "Rule engine indicates lower priority, while ML provides a supplementary probability estimate."

    # 🔗 Assemble exact requested format
    return (
        f"{rule_score} – {label}.\n\n"
        f"Rule-Based Explanation:\n{rule_text}\n\n"
        f"📊 ML Insight:\n{ml_insight}\n\n"
        f"🧠 Summary:\n{summary}"
    )


def run():
    print("API:", os.getenv("CRM_API_KEY"))
    print("URL:", os.getenv("CRM_BASE_URL"))

    auth = CRMAuth(cookie_string=os.getenv("CRM_COOKIE"))
    client = CRMClient(base_url=os.getenv("CRM_BASE_URL"), auth=auth)

    fetcher = LeadFetcher()
    pusher = ScorePusher(client)

    extractor = FieldExtractor()
    cleaner = SignalCleaner()
    quality_layer = FeatureQualityLayer()
    signal_builder = SignalBuilder()
    fusion = FusionLayer()

    # 🆕 ADDED: Initialize ML refinement layer
    ml_refiner = MLRefinementLayer()

    rules = RuleParser().load_rules("rules.json")
    executor = RuleExecutor()

    leads = fetcher.fetch_leads()
    print(f"\n📦 TOTAL LEADS FETCHED: {len(leads)}")

    if not leads:
        print("⚠️ No leads fetched")
        return

    processed = 0

    for lead in leads:
        lead_id = str(
            lead.get("id") or lead.get("sf_id") or lead.get("_id") or "unknown"
        )

        print(f"\n==============================\n🚀 PROCESSING LEAD: {lead_id}\n==============================")

        try:
            # 1-6. Engine pipeline (UNCHANGED)
            observations = extractor.extract_all_fields(lead)
            observations = cleaner.clean(observations)
            quality = quality_layer.compute(observations)
            signals = signal_builder.build(observations, quality)
            triggers = executor.debug_execute(signals, rules)
            result = fusion.compute(triggers, quality)

            # 🔑 EXTRACT RULE SCORE & LABEL
            rule_score = result.get("final_score", 0)
            label = result.get("classification", "🔵 Cold Lead")
            breakdown = result.get("breakdown", "")

            # 🤖 ML REFINEMENT (INFORMATIONAL ONLY)
            ml_out = ml_refiner.refine(observations, rule_score, debug=True)
            ml_prob = round(ml_out["ml_probability"] * 100, 1)

            # ✅ FORMAT EXACT POLISHED OUTPUT
            crm_output = format_crm_output(rule_score, label, breakdown, ml_prob)

            print(f"📏 Rule Score: {rule_score:.0f} | 🤖 ML Prob: {ml_prob}% | 🏷️ Label: {label}")
            print("\n🧾 CRM OUTPUT:")
            print(crm_output)

            payload = {
                "ai_lead_score_test": rule_score,
                "ai_label_test": label.replace("🔥 ", "").replace("🟡 ", "").replace("🔵 ", ""),
                "ai_confidence_test": int(rule_score),  # Maps cleanly to rule strength
                "ai_explanation_test": crm_output,
                "ml_conversion_probability": ml_prob,
                "ml_confidence_level": "Low"  # Explicitly capped per spec
            }

            print("\n📤 SHADOW PUSH:", payload)

            # 🔒 ISOLATE PUSHER CRASH
            try:
                pusher.push_score(lead_id, payload)
                print(f"✅ Shadow pushed for {lead_id}")
            except AttributeError as e:
                print(f"⚠️ Pusher crashed on .total_score: {e} (Score logged anyway)")
            except Exception as e:
                print(f"⚠️ Pusher error: {e}")

            processed += 1

        except Exception as e:
            print(f"❌ Failed lead {lead_id}: {e}")

    print(f"\n🔥 TOTAL LEADS PROCESSED: {processed}")


if __name__ == "__main__":
    run()