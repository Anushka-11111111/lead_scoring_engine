class SignalWeighter:
    """
    Responsible for assigning importance weights
    to semantic signals.

    Purpose:
    Not all signals should contribute equally
    to lead scoring.

    Example:
    - Behavioral activity may be highly valuable
    - Data quality signals may be less impactful
    - Unknown signals should contribute minimally

    This class converts semantic meaning into
    scoring importance.

    Why weighting matters:
    Weighting enables:
    - Better scoring accuracy
    - Smarter prioritization
    - Quality-aware intelligence
    - More realistic lead ranking

    Example:
        behavior signal
        → stronger contribution

        unknown signal
        → weaker contribution
    """

    def get_weight(self, signal_type: str, value) -> float:
        """
        Computes the importance weight for a signal.

        Weight calculation considers:
        - Semantic signal category
        - Value characteristics
        - Signal reliability

        Args:
            signal_type (str):
                Semantic classification of the signal.

                Examples:
                - fit
                - behavior
                - quality
                - unknown

            value:
                Original CRM field value.

        Returns:
            float:
                Final calculated signal weight.
        """

        # --------------------------------------------------
        # Base weights by semantic category
        # --------------------------------------------------
        #
        # Higher weight = more scoring influence
        #
        # Examples:
        # behavior → stronger intent indicator
        # quality  → supportive signal
        # unknown  → weak/untrusted signal
        # --------------------------------------------------
        base_weights = {

            # ICP/profile relevance
            "fit": 1.0,

            # Engagement/intent signals
            "behavior": 1.2,

            # Data quality/completeness
            "quality": 0.8,

            # Unrecognized/uncertain signals
            "unknown": 0.5
        }

        # Retrieve base weight
        #
        # Fallback = 0.5 for unknown categories
        weight = base_weights.get(signal_type, 0.5)

        # --------------------------------------------------
        # Numeric signal boost
        # --------------------------------------------------
        #
        # Numeric values often represent:
        # - probabilities
        # - engagement scores
        # - activity counts
        # - predictive strength
        #
        # These tend to carry stronger meaning.
        # --------------------------------------------------
        if isinstance(value, (int, float)):

            # Increase importance
            weight *= 1.2

        # --------------------------------------------------
        # Null penalty
        # --------------------------------------------------
        #
        # Missing values reduce signal reliability.
        #
        # Example:
        # Empty phone number
        # → weaker confidence
        # --------------------------------------------------
        if value is None:

            # Reduce contribution significantly
            weight *= 0.5

        # Final computed weight
        return weight
