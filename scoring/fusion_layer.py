from typing import List, Dict
import math


class FusionLayer:
    """
    Advanced score fusion and intelligence layer.

    Purpose:
    Combines:
    - rule triggers
    - feature quality
    - behavioral signals
    - recency
    - geography
    - confidence logic

    into ONE final lead score.

    This is the "brain" of the scoring system.

    Why FusionLayer exists:
    Individual rules alone are not enough.

    Example:
        A lead may have:
        - high pipeline probability
        BUT
        - fake email
        - missing phone
        - old activity

    FusionLayer intelligently balances:
    - positive signals
    - penalties
    - data quality
    - contradictions
    - synergy effects

    Final Outputs:
    - Final lead score
    - Lead classification
    - Confidence score
    - Human-readable breakdown
    """

    def __init__(self):

        # ==================================================
        # 🎯 RULE IMPORTANCE MULTIPLIERS
        # ==================================================
        #
        # Some rules are more important than others.
        #
        # Example:
        # "High Pipeline Probability"
        # is MUCH stronger than:
        # "Has Email"
        #
        # These multipliers amplify/reduce
        # rule influence.
        # ==================================================
        self.rule_multipliers = {

            "High Pipeline Probability": 1.4,

            "Has Email": 1.15,

            "Has Phone": 1.15,

            "Facebook Source": 0.9,

            "Valid Email": 1.25,

            "Valid Phone": 1.25,

            "High Value Geography": 1.3
        }

        # ==================================================
        # ❌ STATIC PENALTIES
        # ==================================================
        #
        # Negative signals directly reduce score.
        #
        # Example:
        # Missing contact information
        # is a strong sales blocker.
        # ==================================================
        self.penalties = {

            "Missing Email": -15,

            "Invalid Email": -10,

            "Invalid Phone": -10
        }

        # ==================================================
        # 🧠 RULE → FEATURE QUALITY MAPPING
        # ==================================================
        #
        # Maps rules to the CRM fields
        # responsible for them.
        #
        # Used for:
        # quality-aware scoring
        # ==================================================
        self.rule_quality_map = {

            "Has Email": [
                "sf_email"
            ],

            "Has Phone": [
                "sf_phone_number.value"
            ],

            "Recent Lead": [
                "sf_created_at"
            ],

            "High Pipeline Probability": [
                "sf_pipeline_stage.winprobability"
            ],

            "Valid Email": [
                "sf_email"
            ],

            "Valid Phone": [
                "sf_phone_number.value"
            ]
        }

        # ==================================================
        # 🌍 HIGH-VALUE COUNTRIES
        # ==================================================
        #
        # Geographic prioritization.
        #
        # Helps sales focus on:
        # - premium markets
        # - higher purchasing power regions
        # ==================================================
        self.high_value_countries = [

            "usa",
            "united states",

            "uk",
            "united kingdom",

            "canada",

            "germany",

            "australia"
        ]

    # =====================================================
    # 🎯 MAIN SCORING ENGINE
    # =====================================================
    def compute(
        self,
        triggers: List,
        quality: Dict,
        observations: Dict = None
    ):
        """
        Main fusion engine.

        Combines:
        - rule triggers
        - quality metrics
        - observations
        - dynamic scoring
        - penalties
        - synergy bonuses

        into ONE final lead intelligence output.

        Returns:
            {
                final_score,
                classification,
                confidence,
                breakdown
            }
        """

        observations = observations or {}

        # --------------------------------------------------
        # No triggered rules
        # --------------------------------------------------
        if not triggers:

            return {

                "final_score": 0,

                "classification": "🔵 Cold Lead",

                "confidence": 0.0,

                "breakdown":
                    "No strong signals detected"
            }

        # Final accumulated score
        total_score = 0

        # Human-readable explanation log
        breakdown_parts = []

        # Tracks triggered rule names
        triggered_names = set()

        # ==================================================
        # 🧠 CONTINUOUS DYNAMIC SCORING
        # ==================================================
        for t in triggers:

            name = getattr(t, "name", "Unknown")

            base_score = float(
                getattr(t, "score", 0)
            )

            triggered_names.add(name)

            # ==================================================
            # ❌ STATIC PENALTIES
            # ==================================================
            if name in self.penalties:

                penalty = self.penalties[name]

                total_score += penalty

                breakdown_parts.append(
                    f"{name} ({penalty})"
                )

                continue

            # ==================================================
            # 🎯 RULE MULTIPLIER
            # ==================================================
            multiplier = self.rule_multipliers.get(
                name,
                1.0
            )

            # ==================================================
            # 🧠 DYNAMIC SIGNAL STRENGTH
            # ==================================================
            #
            # Example:
            # 90% win probability
            # should be stronger than:
            # 60%
            # ==================================================
            dynamic_strength = (
                self._compute_dynamic_strength(
                    name,
                    observations
                )
            )

            # ==================================================
            # 📊 INITIAL SCORE
            # ==================================================
            score = (
                base_score
                * multiplier
                * dynamic_strength
            )

            # ==================================================
            # 🧠 QUALITY SCALING
            # ==================================================
            #
            # High-quality data should
            # contribute more strongly.
            # ==================================================
            quality_score = self._get_quality_score(
                name,
                quality
            )

            if quality_score is not None:

                # --------------------------------------------------
                # Normalize quality if stored as 0–100
                # --------------------------------------------------
                if quality_score > 1:
                    quality_score /= 100

                # --------------------------------------------------
                # Quality-aware multiplier
                #
                # Example:
                # 0.9 quality → 1.4 multiplier
                # --------------------------------------------------
                quality_multiplier = (
                    0.5 + quality_score
                )

                score *= quality_multiplier

                breakdown_parts.append(
                    f"{name} quality "
                    f"x{quality_multiplier:.2f}"
                )

            # ==================================================
            # ⏳ RECENCY DECAY
            # ==================================================
            #
            # Older leads become weaker.
            # ==================================================
            recency_factor = (
                self._compute_recency_factor(
                    observations
                )
            )

            score *= recency_factor

            # ==================================================
            # 🌍 GEO PRIORITIZATION
            # ==================================================
            geo_multiplier = self._geo_multiplier(
                observations
            )

            score *= geo_multiplier

            # Final rounded rule score
            final_score = round(score, 2)

            total_score += final_score

            breakdown_parts.append(
                f"{name} (+{final_score})"
            )

        # ==================================================
        # ⚡ SYNERGY BONUSES
        # ==================================================
        #
        # Some combinations of signals
        # are stronger together.
        # ==================================================
        synergy_bonus = 0

        # Strong contactability
        if (
            "Has Email" in triggered_names
            and "Has Phone" in triggered_names
        ):

            synergy_bonus += 7

            breakdown_parts.append(
                "Strong contactability (+7)"
            )

        # Sales-ready lead
        if (
            "High Pipeline Probability"
            in triggered_names
            and "Has Phone" in triggered_names
        ):

            synergy_bonus += 6

            breakdown_parts.append(
                "Sales-ready lead (+6)"
            )

        # Verified contact information
        if (
            "Valid Email" in triggered_names
            and "Valid Phone" in triggered_names
        ):

            synergy_bonus += 5

            breakdown_parts.append(
                "Verified contact data (+5)"
            )

        total_score += synergy_bonus

        # ==================================================
        # ⚠️ CONTRADICTION DETECTION
        # ==================================================
        #
        # Detects unrealistic/incomplete leads.
        #
        # Example:
        # High pipeline probability
        # but NO contact info.
        # ==================================================
        contradiction_penalty = 0

        if (
            "High Pipeline Probability"
            in triggered_names
            and "Has Email"
            not in triggered_names
        ):
            contradiction_penalty += 8

        if (
            "High Pipeline Probability"
            in triggered_names
            and "Has Phone"
            not in triggered_names
        ):
            contradiction_penalty += 8

        if contradiction_penalty > 0:

            total_score -= contradiction_penalty

            breakdown_parts.append(
                f"Signal contradiction "
                f"(-{contradiction_penalty})"
            )

        # ==================================================
        # 🧊 LOW ENGAGEMENT DAMPENING
        # ==================================================
        #
        # Weak engagement signals
        # slightly reduce score.
        # ==================================================
        if (
            "Has Email" not in triggered_names
            and "Recent Lead"
            not in triggered_names
        ):

            total_score -= 5

            breakdown_parts.append(
                "Low engagement (-5)"
            )

        # ==================================================
        # 🧠 FINAL NORMALIZATION
        # ==================================================
        #
        # Clamp score into:
        # 0 → 100
        # ==================================================
        total_score = max(
            0,
            min(round(total_score), 100)
        )

        # Final lead category
        classification = self._classify(
            total_score
        )

        # Confidence engine
        confidence = self._confidence(
            total_score,
            triggers,
            quality
        )

        # ==================================================
        # FINAL OUTPUT
        # ==================================================
        return {

            "final_score": total_score,

            "classification": classification,

            "confidence": confidence,

            "breakdown":
                ", ".join(breakdown_parts)
        }

    # =====================================================
    # 🧠 DYNAMIC SIGNAL STRENGTH
    # =====================================================
    def _compute_dynamic_strength(
        self,
        rule_name,
        observations
    ):
        """
        Computes real-time signal strength.

        Stronger values contribute
        more aggressively.

        Example:
        Higher win probability
        → stronger signal
        """

        # --------------------------------------------------
        # Pipeline probability scaling
        # --------------------------------------------------
        if rule_name == "High Pipeline Probability":

            prob = observations.get(
                "sf_pipeline_stage.winprobability",
                0
            )

            try:
                prob = float(prob)

            except:
                prob = 0

            # Dynamic scaling range:
            # 0.5 → 2.0
            return min(
                max(prob / 50, 0.5),
                2.0
            )

        # --------------------------------------------------
        # Lead recency scaling
        # --------------------------------------------------
        if rule_name == "Recent Lead":

            recency_quality = observations.get(
                "recency_quality",
                50
            )

            try:
                recency_quality = float(
                    recency_quality
                )

            except:
                recency_quality = 50

            return min(
                max(recency_quality / 50, 0.5),
                2.0
            )

        return 1.0

    # =====================================================
    # 🌍 GEO MULTIPLIER
    # =====================================================
    def _geo_multiplier(self, observations):
        """
        Applies country-based prioritization.
        """

        country = str(
            observations.get(
                "sf_country",
                ""
            )
        ).lower()

        # Premium markets
        if country in self.high_value_countries:
            return 1.25

        # Medium-value market
        if country == "india":
            return 1.10

        # Other known countries
        if country:
            return 0.95

        return 1.0

    # =====================================================
    # ⏳ RECENCY DECAY
    # =====================================================
    def _compute_recency_factor(
        self,
        observations
    ):
        """
        Applies exponential decay
        for aging leads.

        Older leads become less valuable.
        """

        days_old = observations.get(
            "lead_age_days"
        )

        if days_old is None:
            return 1.0

        try:
            days_old = float(days_old)

        except:
            return 1.0

        # --------------------------------------------------
        # Exponential decay curve
        # --------------------------------------------------
        decay = math.exp(-days_old / 45)

        # Safety clamp
        return max(
            0.55,
            min(decay, 1.25)
        )

    # =====================================================
    # 🧠 QUALITY HELPER
    # =====================================================
    def _get_quality_score(
        self,
        rule_name,
        quality
    ):
        """
        Retrieves average quality score
        associated with a rule.
        """

        features = self.rule_quality_map.get(
            rule_name
        )

        if not features:
            return None

        scores = [

            quality.get(f)

            for f in features

            if f in quality
        ]

        if not scores:
            return None

        return sum(scores) / len(scores)

    # =====================================================
    # 🏷️ LEAD CLASSIFICATION
    # =====================================================
    def _classify(self, score):
        """
        Converts score into
        business-friendly lead category.
        """

        if score >= 80:
            return "🔥 Hot Lead"

        elif score >= 50:
            return "🟡 Warm Lead"

        return "🔵 Cold Lead"

    # =====================================================
    # 🧠 CONFIDENCE ENGINE
    # =====================================================
    def _confidence(
        self,
        score,
        triggers,
        quality
    ):
        """
        Computes overall confidence score.

        Confidence depends on:
        - total score
        - trigger count
        - average quality
        """

        # Total triggered signals
        signal_count = len(triggers)

        quality_values = []

        # --------------------------------------------------
        # Normalize quality values
        # --------------------------------------------------
        for v in quality.values():

            try:
                v = float(v)

                if v > 1:
                    v /= 100

                quality_values.append(v)

            except:
                continue

        # Average feature quality
        avg_quality = (

            sum(quality_values)
            / len(quality_values)

            if quality_values
            else 0.5
        )

        # ==================================================
        # RICH CONFIDENCE FORMULA
        # ==================================================
        confidence = (

            # score quality
            (score / 100) * 0.5

            +

            # signal richness
            min(signal_count / 10, 1.0) * 0.3

            +

            # feature quality
            avg_quality * 0.2
        )

        # Final percentage confidence
        return round(
            min(confidence, 1.0) * 100,
            2
        )