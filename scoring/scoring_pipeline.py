```python id="m8x2kp"
class ScoreResult:
    """
    Lightweight final scoring output object.

    Purpose:
    Stores the final scoring result generated
    by the scoring pipeline.

    Contains:
    - lead ID
    - total score
    - lead classification
    - human-readable explanation

    This object is useful for:
    - CRM display
    - debugging
    - API responses
    - console output
    """

    def __init__(
        self,
        lead_id,
        total_score,
        classification,
        breakdown
    ):

        # Unique lead identifier
        self.lead_id = lead_id

        # Final computed score
        self.total_score = total_score

        # Lead category
        # Example:
        # 🔥 Hot Lead
        self.classification = classification

        # Human-readable explanation
        self.breakdown = breakdown

    # --------------------------------------------------
    # String formatter
    #
    # Controls how object prints to console/logs.
    #
    # VERY IMPORTANT:
    # Python automatically uses __str__()
    # when printing objects.
    # --------------------------------------------------
    def __str__(self):

        return f"""
📊 CRM OUTPUT:
{self.total_score} – {self.classification}

{self.breakdown}
"""


class ScoringPipeline:
    """
    Final scoring orchestration layer.

    Purpose:
    Converts rule triggers into:
    - total score
    - classification
    - readable explanation

    Pipeline Flow:
        Rule Triggers
              ↓
        Score Aggregation
              ↓
        Classification
              ↓
        Explanation Builder
              ↓
        ScoreResult
    """

    def __init__(self):
        """
        Pipeline initializer.

        Currently empty but reserved for:
        - future configs
        - ML integration
        - scoring calibration
        - dependency injection
        """
        pass

    # ==================================================
    # 🎯 MAIN SCORING FUNCTION
    # ==================================================
    def run(
        self,
        lead_id,
        signals,
        triggers
    ):
        """
        Main scoring execution method.

        Args:
            lead_id:
                Unique lead identifier

            signals:
                Semantic signals generated earlier
                in the intelligence pipeline

            triggers:
                Triggered rules from RuleExecutor

        Returns:
            ScoreResult object
        """

        # --------------------------------------------------
        # Final accumulated score
        # --------------------------------------------------
        total_score = 0

        # --------------------------------------------------
        # Aggregate all trigger scores
        # --------------------------------------------------
        for t in triggers:

            total_score += t.score

        # --------------------------------------------------
        # Determine lead category
        # --------------------------------------------------
        classification = self._classify(
            total_score
        )

        # --------------------------------------------------
        # Build human-readable explanation
        # --------------------------------------------------
        breakdown = self._build_paragraph(
            triggers,
            classification
        )

        # --------------------------------------------------
        # Return structured final result
        # --------------------------------------------------
        return ScoreResult(

            lead_id=lead_id,

            total_score=total_score,

            classification=classification,

            breakdown=breakdown
        )

    # ==================================================
    # 🔥 LEAD CLASSIFICATION ENGINE
    # ==================================================
    def _classify(self, score):
        """
        Converts numeric score into
        business-friendly lead category.

        Score Ranges:
            80+  → Hot
            50+  → Warm
            <50  → Cold
        """

        # Highly qualified lead
        if score >= 80:

            return "🔥 Hot Lead"

        # Moderately promising lead
        elif score >= 50:

            return "🟡 Warm Lead"

        # Weak/unqualified lead
        else:

            return "🔵 Cold Lead"

    # ==================================================
    # 📊 HUMAN-READABLE EXPLANATION BUILDER
    # ==================================================
    def _build_paragraph(
        self,
        triggers,
        classification
    ):
        """
        Converts technical rule triggers into
        natural language explanation.

        Why important:
        Business users should understand:
        - WHY a lead scored highly
        - WHAT signals contributed
        - WHICH rules triggered

        Example:
        "This lead is classified as hot lead
        due to valid email (+10),
        recent activity (+15),
        and high pipeline probability (+20)."
        """

        # --------------------------------------------------
        # No triggers fallback
        # --------------------------------------------------
        if not triggers:

            return (
                "No significant signals were "
                "detected for this lead."
            )

        # Individual explanation fragments
        parts = []

        # --------------------------------------------------
        # Convert triggers into readable phrases
        # --------------------------------------------------
        for t in triggers:

            # Prefer explicit reason if available
            label = (

                t.reason

                if t.reason

                else t.name
            ).lower()

            # Example:
            # valid email (+10)
            parts.append(
                f"{label} (+{t.score})"
            )

        # --------------------------------------------------
        # Natural sentence formatting
        # --------------------------------------------------

        # Single reason
        if len(parts) == 1:

            sentence = parts[0]

        # Multiple reasons
        else:

            sentence = (

                ", ".join(parts[:-1])

                + f", and {parts[-1]}"
            )

        # --------------------------------------------------
        # Remove emojis for clean sentence grammar
        # --------------------------------------------------
        clean_class = (

            classification

            .replace("🔥 ", "")

            .replace("🟡 ", "")

            .replace("🔵 ", "")

            .lower()
        )

        # --------------------------------------------------           
        # Final explanation paragraph
        # --------------------------------------------------
        return (

            f"This lead is classified as "

            f"{clean_class} "

            f"due to {sentence}."
        )
```
