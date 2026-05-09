import re
from datetime import datetime
from typing import Dict


class FeatureQualityLayer:
    """
    Computes quality/confidence scores for important CRM lead signals.

    Purpose:
    - Measure trustworthiness of lead data
    - Improve scoring reliability
    - Detect fake/spam/demo/test leads
    - Generate ML-friendly normalized quality features

    Each method returns a quality score between:
        0   = very poor quality
        100 = extremely high quality

    These quality scores can later be:
    - Used directly in rule-based scoring
    - Fed into ML models as engineered features
    - Used for explainability in AI summaries
    """

    # --------------------------------------------------
    # 📧 EMAIL QUALITY
    # --------------------------------------------------
    def email_quality(self, email: str) -> float:
        """
        Evaluates the quality and trustworthiness of an email address.

        Scoring Factors:
        - Valid email format
        - Disposable email detection
        - Business vs free email domains
        - Fake/test/demo keyword detection

        Args:
            email (str):
                Lead email address.

        Returns:
            float:
                Quality score between 0–100.
        """

        # Missing email
        if not email:
            return 0

        # Normalize email
        email = str(email).strip().lower()

        # ----------------------------------------
        # Basic email format validation
        # ----------------------------------------
        # Example valid:
        # john@company.com
        #
        # Example invalid:
        # john@@company
        # ----------------------------------------
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return 10

        # Base confidence score
        score = 60

        # ----------------------------------------
        # Disposable / temporary email detection
        # These are commonly used for spam/demo leads
        # ----------------------------------------
        disposable_domains = [
            "mailinator.com",
            "tempmail.com",
            "10minutemail.com",
            "guerrillamail.com",
            "yopmail.com"
        ]

        # Extract domain
        domain = email.split("@")[-1]

        # Penalize disposable domains
        if domain in disposable_domains:
            score -= 40
        else:
            score += 15

        # ----------------------------------------
        # Free email providers
        # Business domains are usually higher intent
        # ----------------------------------------
        free_domains = [
            "gmail.com",
            "yahoo.com",
            "hotmail.com",
            "outlook.com"
        ]

        # Boost business/corporate emails
        if domain not in free_domains:
            score += 20

        # ----------------------------------------
        # Detect fake/test/demo emails
        # ----------------------------------------
        suspicious_words = [
            "test",
            "fake",
            "demo",
            "sample",
            "dummy"
        ]

        if any(word in email for word in suspicious_words):
            score -= 30

        # Ensure score stays within 0–100
        return min(100, max(0, score))

    # --------------------------------------------------
    # ☎️ PHONE QUALITY
    # --------------------------------------------------
    def phone_quality(self, phone: str) -> float:
        """
        Evaluates the reliability of a phone number.

        Scoring Factors:
        - Minimum length validation
        - Spam/repeated digit detection
        - Fake number pattern detection

        Args:
            phone (str):
                Lead phone number.

        Returns:
            float:
                Quality score between 0–100.
        """

        # Missing phone number
        if not phone:
            return 0

        # Remove all non-numeric characters
        # Example:
        # "+91-98765-43210" → "919876543210"
        phone = re.sub(r"\D", "", str(phone))

        # Very short numbers are suspicious
        if len(phone) < 10:
            return 10

        # Base score
        score = 60

        # ----------------------------------------
        # Repeated digit spam check
        # Example:
        # 1111111111
        # 9999999999
        # ----------------------------------------
        if len(set(phone)) < 3:
            score -= 35

        # Good length range boost
        if 10 <= len(phone) <= 13:
            score += 20

        # ----------------------------------------
        # Fake/spam phone patterns
        # ----------------------------------------
        fake_patterns = [
            "123456",
            "000000",
            "999999",
            "111111"
        ]

        if any(p in phone for p in fake_patterns):
            score -= 30

        return min(100, max(0, score))

    # --------------------------------------------------
    # ⏳ RECENCY QUALITY
    # --------------------------------------------------
    def recency_quality(self, created_at: str) -> float:
        """
        Measures how recent the lead creation timestamp is.

        Newer leads are generally considered:
        - More active
        - Higher intent
        - Easier to convert

        Args:
            created_at (str):
                ISO timestamp from CRM.

        Returns:
            float:
                Recency quality score.
        """

        # Missing timestamp
        if not created_at:
            return 40

        try:
            # Convert ISO string → datetime object
            created = datetime.fromisoformat(
                str(created_at).replace("Z", "")
            )

            # Compute age in days
            diff_days = (
                datetime.utcnow() - created
            ).days

        # Invalid timestamp format
        except:
            return 50

        # ----------------------------------------
        # Freshness scoring
        # More recent = higher score
        # ----------------------------------------
        if diff_days <= 1:
            return 100

        elif diff_days <= 3:
            return 90

        elif diff_days <= 7:
            return 75

        elif diff_days <= 14:
            return 60

        elif diff_days <= 30:
            return 40

        # Old/stale leads
        return 20

    # --------------------------------------------------
    # 🌍 COUNTRY QUALITY
    # --------------------------------------------------
    def country_quality(self, country: str) -> float:
        """
        Assigns a quality score based on country/market value.

        Useful for:
        - ICP matching
        - Revenue prioritization
        - Geographic segmentation

        Args:
            country (str):
                Lead country.

        Returns:
            float:
                Geographic quality score.
        """

        # Unknown country
        if not country:
            return 50

        # Normalize input
        country = str(country).strip().lower()

        # High-value markets
        high_value = [
            "usa",
            "united states",
            "uk",
            "united kingdom",
            "canada",
            "germany",
            "australia"
        ]

        # Medium-value markets
        medium_value = [
            "india",
            "singapore",
            "uae"
        ]

        # Premium geo markets
        if country in high_value:
            return 95

        # Medium-priority markets
        if country in medium_value:
            return 75

        # Default market score
        return 55

    # --------------------------------------------------
    # 📊 PIPELINE QUALITY
    # --------------------------------------------------
    def pipeline_quality(self, probability) -> float:
        """
        Converts CRM pipeline win probability
        into a normalized quality score.

        Example:
        CRM probability = 80%
        → High-quality opportunity

        Args:
            probability:
                CRM pipeline win probability.

        Returns:
            float:
                Pipeline quality score.
        """

        # Safe numeric conversion
        try:
            probability = float(probability)

        # Invalid probability
        except:
            return 50

        # ----------------------------------------
        # Probability bucket scoring
        # ----------------------------------------
        if probability >= 80:
            return 100

        elif probability >= 60:
            return 85

        elif probability >= 40:
            return 70

        elif probability >= 20:
            return 50

        return 30

    # --------------------------------------------------
    # 🧠 MAIN QUALITY ENGINE
    # --------------------------------------------------
    def compute(self, signal_dict: Dict) -> Dict:
        """
        Main orchestration layer that computes
        all feature quality scores together.

        This acts as the central feature engineering
        quality layer before:
        - Rule scoring
        - ML prediction
        - AI explanations

        Args:
            signal_dict (Dict):
                Flattened CRM signals.

        Returns:
            Dict:
                Map of signal quality scores.
        """

        # ----------------------------------------
        # Individual feature quality calculations
        # ----------------------------------------

        # Email quality
        email_quality = self.email_quality(
            signal_dict.get("sf_email")
        )

        # Phone quality
        phone_quality = self.phone_quality(
            signal_dict.get("sf_phone_number.value")
        )

        # Lead freshness quality
        recency_quality = self.recency_quality(
            signal_dict.get("sf_created_at")
        )

        # Geographic market quality
        country_quality = self.country_quality(
            signal_dict.get("sf_country")
        )

        # CRM opportunity/pipeline quality
        pipeline_quality = self.pipeline_quality(
            signal_dict.get(
                "sf_pipeline_stage.winprobability"
            )
        )

        # --------------------------------------------------
        # 🧠 FINAL QUALITY MAP
        # IMPORTANT:
        # Keys should match actual signal paths
        # so downstream systems can directly access them.
        # --------------------------------------------------
        return {

            # Original signal-linked quality scores
            "sf_email": email_quality,
            "sf_phone_number.value": phone_quality,
            "sf_created_at": recency_quality,
            "sf_country": country_quality,
            "sf_pipeline_stage.winprobability": pipeline_quality,

            # Helper engineered features
            # Easier for ML + explainability layers
            "email_quality": email_quality,
            "phone_quality": phone_quality,
            "recency_quality": recency_quality,
            "country_quality": country_quality,
            "pipeline_quality": pipeline_quality
        }