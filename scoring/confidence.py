class ConfidenceCalculator:
    """
    Calculates confidence level for the final lead score.

    Purpose:
    A lead score alone is not enough.

    The system should also indicate:
    "How reliable is this score?"

    Confidence helps measure:
    - Signal coverage
    - Rule match density
    - Data completeness
    - Scoring reliability

    Why confidence matters:
    Two leads may both score 80,
    but one may have:
    - rich behavioral/activity data
    while the other has:
    - minimal information

    Confidence helps distinguish between:
    - strong reliable predictions
    - weak uncertain predictions

    Typical Interpretation:
    --------------------------------------------------
    0.9 - 1.0
        Very high confidence

    0.7 - 0.89
        Good confidence

    0.5 - 0.69
        Moderate confidence

    Below 0.5
        Weak/unreliable prediction
    --------------------------------------------------
    """

    def calculate(self, signals, triggers) -> float:
        """
        Computes confidence score based on
        signal coverage and triggered rules.

        Core idea:
        More meaningful rule matches across
        available signals → higher confidence.

        Formula:
            confidence =
                0.5 + (coverage * 0.5)

        Where:
            coverage =
                triggered_rules / total_signals

        Args:
            signals:
                List of SemanticSignal objects.

            triggers:
                List of triggered RuleTrigger objects.

        Returns:
            float:
                Confidence score between 0.0 and 1.0
        """

        # --------------------------------------------------
        # No signals available
        #
        # Without signals, scoring reliability
        # becomes extremely weak.
        # --------------------------------------------------
        if not signals:
            return 0.0

        # ==================================================
        # SIGNAL COVERAGE
        # ==================================================
        #
        # Measures how many available signals
        # successfully contributed to rule matches.
        #
        # Example:
        # 5 triggers / 10 signals = 0.5 coverage
        # ==================================================
        coverage = len(triggers) / len(signals)

        # --------------------------------------------------
        # Safety cap
        #
        # Prevent confidence from exceeding 1.0
        # --------------------------------------------------
        coverage = min(coverage, 1.0)

        # ==================================================
        # BASIC CONFIDENCE SCALING
        # ==================================================
        #
        # Base confidence starts at:
        # 0.5
        #
        # Then increases proportionally
        # based on rule/signal coverage.
        #
        # Example:
        #
        # coverage = 0.0
        # confidence = 0.5
        #
        # coverage = 1.0
        # confidence = 1.0
        # ==================================================
        confidence = 0.5 + (coverage * 0.5)

        # Rounded for cleaner output/UI readability
        return round(confidence, 2)