from typing import Any
import re


class SignalClassifier:
    """
    Responsible for semantically classifying CRM fields/signals.

    Purpose:
    Raw CRM fields are often unstructured and inconsistent.

    This classifier converts them into meaningful
    business intelligence categories such as:
    - fit
    - behavior
    - quality
    - unknown

    Why this matters:
    Classification enables:
    - Rule-based scoring
    - ML feature grouping
    - Signal prioritization
    - Explainability
    - Confidence estimation

    Example:
        "sf_email"
        → ("fit", 0.9)

        "sf_pipeline_stage.winprobability"
        → ("behavior", 0.85)
    """

    def __init__(self):
        """
        Initializes semantic pattern registries.

        Each registry represents a business meaning category.
        """

        # --------------------------------------------------
        # 🔥 FIT SIGNALS
        # --------------------------------------------------
        #
        # Represents:
        # - Lead identity
        # - Company/profile quality
        # - ICP relevance
        #
        # Examples:
        # - email
        # - company
        # - role/title
        # - pipeline stage
        # --------------------------------------------------
        self.fit_patterns = [
            r"email",
            r"name",
            r"owner",
            r"tag",
            r"status",
            r"pipeline",
            r"stage",
            r"role",
            r"company",
            r"industry",
            r"title",
            r"source"
        ]

        # --------------------------------------------------
        # 🔥 BEHAVIOR SIGNALS
        # --------------------------------------------------
        #
        # Represents:
        # - Lead activity
        # - Engagement
        # - Intent
        # - Pipeline movement
        #
        # Examples:
        # - created_at
        # - updated_at
        # - activity logs
        # - win probability
        # --------------------------------------------------
        self.behavior_patterns = [
            r"winprobability",
            r"assigned",
            r"created",
            r"updated",
            r"activity",
            r"last",
            r"pipeline",
            r"stage",
            r"rottingin",
            r"score"
        ]

        # --------------------------------------------------
        # 🔥 QUALITY SIGNALS
        # --------------------------------------------------
        #
        # Represents:
        # - Data completeness
        # - Contact quality
        # - Geographic information
        #
        # Examples:
        # - phone
        # - address
        # - city/state
        # - country
        # --------------------------------------------------
        self.quality_patterns = [
            r"zipcode",
            r"address",
            r"city",
            r"state",
            r"country",
            r"phone",
            r"email"
        ]

    def classify(self, path: str, value: Any):
        """
        Classifies a CRM field into a semantic category.

        Classification strategy:
        1. Path-based pattern matching
        2. Value-based intelligence
        3. Fallback heuristics

        Args:
            path (str):
                CRM field path.

            value (Any):
                CRM field value.

        Returns:
            tuple:
                (
                    signal_type,
                    confidence_score
                )

        Example:
            ("fit", 0.9)
        """

        # Normalize field path
        path_lower = (path or "").lower()

        # ==================================================
        # FIT CLASSIFICATION
        # ==================================================
        #
        # Detects:
        # - Identity fields
        # - Profile/company fields
        # - ICP-related information
        # ==================================================
        if self._match(path_lower, self.fit_patterns):

            # High confidence semantic classification
            return "fit", 0.9

        # ==================================================
        # BEHAVIOR CLASSIFICATION
        # ==================================================
        #
        # Detects:
        # - Activity
        # - Intent
        # - Engagement
        # - Pipeline movement
        # ==================================================
        if self._match(path_lower, self.behavior_patterns):

            return "behavior", 0.85

        # ==================================================
        # QUALITY CLASSIFICATION
        # ==================================================
        #
        # Detects:
        # - Data hygiene
        # - Completeness
        # - Contact/location quality
        # ==================================================
        if self._match(path_lower, self.quality_patterns):

            return "quality", 0.8

        # ==================================================
        # VALUE-BASED INTELLIGENCE
        # ==================================================
        #
        # If path matching fails,
        # infer meaning from the actual value.
        # ==================================================

        # --------------------------------------------------
        # Numeric intelligence
        # --------------------------------------------------
        #
        # High numeric values often indicate:
        # - Intent strength
        # - Probability
        # - Activity scoring
        # --------------------------------------------------
        if isinstance(value, (int, float)):

            # Strong/high numeric signal
            if value >= 50:
                return "behavior", 0.9

            # Moderate numeric signal
            return "behavior", 0.6

        # --------------------------------------------------
        # Structured object intelligence
        # --------------------------------------------------
        #
        # CRM objects containing:
        # - label
        # - name
        #
        # often represent profile/fit information.
        # --------------------------------------------------
        if isinstance(value, dict):

            if "label" in value or "name" in value:
                return "fit", 0.8

        # --------------------------------------------------
        # String-based heuristics
        # --------------------------------------------------
        if isinstance(value, str):

            # Numeric string
            #
            # Example:
            # "85"
            if value.isdigit():
                return "behavior", 0.7

            # Email detection
            #
            # Strong identity signal
            if "@" in value:
                return "fit", 0.9

        # ==================================================
        # Unknown fallback
        # ==================================================
        #
        # Low-confidence classification when no
        # meaningful semantic inference is possible.
        # ==================================================
        return "unknown", 0.2

    def _match(self, text: str, patterns: list) -> bool:
        """
        Helper method for regex-based pattern matching.

        Args:
            text (str):
                Input text to evaluate.

            patterns (list):
                List of regex patterns.

        Returns:
            bool:
                True if ANY pattern matches.
        """

        return any(re.search(p, text) for p in patterns)