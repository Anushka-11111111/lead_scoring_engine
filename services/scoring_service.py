from adapters.signal_cleaner import SignalCleaner
from core_contracts.feature_quality import FeatureQualityLayer
from scoring.fusion_layer import FusionLayer
from scoring.ml_refinement import MLRefinementLayer

from adapters.field_extractor import FieldExtractor
from intelligence.signal_builder import SignalBuilder
from rules_engine.rule_parser import RuleParser
from rules_engine.rule_executor import RuleExecutor


class ScoringService:

    def __init__(self):

        self.extractor = FieldExtractor()
        self.cleaner = SignalCleaner()
        self.quality_layer = FeatureQualityLayer()
        self.signal_builder = SignalBuilder()
        self.fusion = FusionLayer()
        self.ml_refiner = MLRefinementLayer()

        self.rules = RuleParser().load_rules("rules.json")
        self.executor = RuleExecutor()

    def score_lead(self, lead):

        observations = self.extractor.extract_all_fields(lead)

        observations = self.cleaner.clean(observations)

        quality = self.quality_layer.compute(observations)

        signals = self.signal_builder.build(observations, quality)

        triggers = self.executor.debug_execute(signals, self.rules)

        result = self.fusion.compute(triggers, quality)

        rule_score = result.get("final_score", 0)

        label = result.get("classification", "Cold Lead")

        breakdown = result.get("breakdown", "")

        ml_out = self.ml_refiner.refine(
            observations,
            rule_score,
            debug=True
        )

        ml_prob = round(ml_out["ml_probability"] * 100, 1)

        return {
            "lead": lead,
            "rule_score": rule_score,
            "label": label,
            "breakdown": breakdown,
            "ml_probability": ml_prob
        }