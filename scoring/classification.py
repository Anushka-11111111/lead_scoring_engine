```python id="u6pdxm"
class Classifier:
    """
    Final lead classification engine.

    Purpose:
    Converts a numerical lead score into a
    human-readable lead category.

    Why classification matters:
    Sales and business teams usually work with
    categories rather than raw scores.

    Example:
        92 → "hot"
        58 → "warm"
        18 → "cold"

    These categories help:
    - Prioritize outreach
    - Route leads automatically
    - Trigger workflows
    - Improve CRM visibility
    - Simplify decision-making

    Typical Business Meaning:
    --------------------------------------------------
    hot:
        High-intent / high-priority lead
        Immediate sales attention recommended

    warm:
        Moderate interest or partial qualification
        Requires nurturing/follow-up

    cold:
        Low engagement or weak qualification
        Low sales priority
    --------------------------------------------------
    """

    def classify(self, total_score: float) -> str:
        """
        Converts a total lead score into
        a lead classification label.

        Args:
            total_score (float):
                Final aggregated lead score.

        Returns:
            str:
                Lead category:
                - hot
                - warm
                - cold
        """

        # ==================================================
        # HOT LEAD
        # ==================================================
        #
        # High-priority lead with:
        # - strong intent
        # - high engagement
        # - good qualification
        #
        # Recommended action:
        # Immediate sales follow-up
        # ==================================================
        if total_score >= 80:
            return "hot"

        # ==================================================
        # WARM LEAD
        # ==================================================
        #
        # Moderately qualified lead.
        #
        # May require:
        # - nurturing
        # - additional engagement
        # - qualification calls
        # ==================================================
        if total_score >= 40:
            return "warm"

        # ==================================================
        # COLD LEAD
        # ==================================================
        #
        # Weak engagement or low qualification.
        #
        # Lower sales priority.
        # ==================================================
        return "cold"
```
