from typing import List
from core_contracts.rule_trigger import RuleTrigger


class ScoreAggregator:
    """
    Combines all triggered rule scores into
    final category-wise scoring totals.

    Purpose:
    Converts multiple RuleTrigger objects into:
    - fit score
    - behavior score
    - quality score
    - penalty score
    - total score
    - explanation breakdown

    This acts as the:
        "score consolidation layer"
    of the lead scoring pipeline.
    """

    def aggregate(
        self,
        triggers: List[RuleTrigger]
    ) -> dict:
        """
        Aggregates all rule trigger results.

        Args:
            triggers:
                List of triggered rules generated
                by RuleExecutor.

        Returns:
            Dictionary containing:
            - category scores
            - final total
            - explanation reasons
        """

        # --------------------------------------------------
        # Initialize category buckets safely
        #
        # Why initialized:
        # prevents missing-key crashes
        # and ensures stable structure.
        # --------------------------------------------------
        scores = {

            # Lead/company fit score
            "fit": 0.0,

            # Engagement/activity score
            "behavior": 0.0,

            # Data quality/completeness score
            "quality": 0.0,

            # Negative scoring penalties
            "penalty": 0.0
        }

        # --------------------------------------------------
        # Human-readable scoring explanations
        #
        # Used for:
        # - debugging
        # - UI explanations
        # - auditability
        # - sales visibility
        # --------------------------------------------------
        reasons = []

        # ==================================================
        # PROCESS EACH TRIGGER
        # ==================================================
        for t in triggers:

            # Trigger category
            category = t.category

            # --------------------------------------------------
            # Safety check
            #
            # Prevents unknown categories
            # from corrupting scoring.
            # --------------------------------------------------
            if category not in scores:
                continue

            # --------------------------------------------------
            # Add trigger score to category bucket
            # --------------------------------------------------
            scores[category] += t.score

            # --------------------------------------------------
            # Store explanation metadata
            #
            # Useful for:
            # - transparency
            # - explainable AI
            # - CRM breakdowns
            # --------------------------------------------------
            reasons.append({

                # Unique rule identifier
                "rule_id": t.rule_id,

                # Human-readable explanation
                "reason": t.reason,

                # Score contribution
                "score": t.score,

                # Signals responsible for trigger
                "matched_signals":
                    t.matched_signals
            })

        # ==================================================
        # FINAL SCORE CALCULATION
        # ==================================================
        #
        # Total score logic:
        #
        # positive categories:
        #   fit
        #   behavior
        #   quality
        #
        # subtract penalties
        # ==================================================
        total = (

            scores["fit"]

            + scores["behavior"]

            + scores["quality"]

            - abs(scores["penalty"])
        )

        # ==================================================
        # FINAL OUTPUT
        # ==================================================
        return {

            # Category breakdowns
            "fit_score":
                scores["fit"],

            "behavior_score":
                scores["behavior"],

            "quality_score":
                scores["quality"],

            "penalty_score":
                scores["penalty"],

            # Final combined score
            "total_score":
                total,

            # Explainability layer
            "reasons":
                reasons
        }