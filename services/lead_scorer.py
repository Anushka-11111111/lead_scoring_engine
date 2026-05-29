from typing import Any, Dict

from adapters.field_extractor import FieldExtractor
from adapters.signal_cleaner import SignalCleaner
from core_contracts.feature_quality import FeatureQualityLayer
from intelligence.signal_builder import SignalBuilder
from rules_engine.rule_parser import RuleParser
from rules_engine.rule_executor import RuleExecutor
from scoring.fusion_layer import FusionLayer
from scoring.ml_refinement import MLRefinementLayer


def _lead_display_fields(lead: Dict[str, Any]) -> Dict[str, str]:
    lead_id = str(
        lead.get("sf_id")
        or lead.get("id")
        or lead.get("_id")
        or "unknown"
    )
    company_name = (
        lead.get("sf_company_name")
        or lead.get("company_name")
        or lead.get("company")
        or lead.get("sf_company")
        or "Unknown Company"
    )
    lead_name = (
        lead.get("sf_first_name")
        or lead.get("name")
        or lead.get("full_name")
        or lead.get("sf_name")
        or "Unknown Lead"
    )
    return {
        "lead_id": lead_id,
        "name": lead_name,
        "company": company_name,
    }


def score_lead(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the full scoring pipeline on one CRM lead record.
    """
    display = _lead_display_fields(lead)

    extractor = FieldExtractor()
    cleaner = SignalCleaner()
    quality_layer = FeatureQualityLayer()
    signal_builder = SignalBuilder()
    fusion = FusionLayer()
    ml_refiner = MLRefinementLayer()
    rules = RuleParser().load_rules("rules.json")
    executor = RuleExecutor()

    observations = extractor.extract_all_fields(lead)
    observations = cleaner.clean(observations)
    quality = quality_layer.compute(observations)
    signals = signal_builder.build(observations, quality)
    triggers = executor.debug_execute(signals, rules)
    result = fusion.compute(triggers, quality)

    rule_score = result.get("final_score", 0)
    label = result.get("classification", "Cold Lead")
    breakdown = result.get("breakdown", "")

    ml_out = ml_refiner.refine(observations, rule_score, debug=True)
    ml_prob = round(ml_out["ml_probability"] * 100, 1)

    return {
        **display,
        "score": rule_score,
        "label": label,
        "breakdown": breakdown,
        "ml_probability": ml_prob,
        "ml_confidence_level": ml_out.get("ml_confidence_level", "Low"),
        "crm_payload": {
            "ai_lead_score_test": rule_score,
            "ai_label_test": label,
            "ai_confidence_test": int(rule_score),
            "ai_explanation_test": breakdown,
            "ml_conversion_probability": ml_prob,
            "ml_confidence_level": ml_out.get("ml_confidence_level", "Low"),
        },
    }
