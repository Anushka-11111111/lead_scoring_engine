from dataclasses import dataclass
from typing import List, Dict


@dataclass
class FinalScore:
    """
    Represents the FINAL scoring output for a lead.

    This is the unified result object produced after all
    scoring layers complete execution.

    It aggregates:
    - Fit scoring
    - Behavioral scoring
    - Data quality scoring
    - Penalty/risk scoring
    - Confidence estimation
    - Explainability reasons

    Purpose:
    - Standardized scoring response object
    - Easier API serialization
    - Cleaner frontend/backend integration
    - Improved explainability and debugging

    Typical Usage:
    - Returned by scoring engine
    - Stored in database
    - Sent to CRM/UI
    - Consumed by AI explanation layer
    """

    # ------------------------------------------------------
    # Unique CRM lead identifier
    # ------------------------------------------------------
    lead_id: str

    # ------------------------------------------------------
    # ICP / Fit Score
    #
    # Measures how closely the lead matches
    # the Ideal Customer Profile (ICP).
    #
    # Examples:
    # - Company size
    # - Geography
    # - Industry
    # - Job title
    # ------------------------------------------------------
    fit_score: float

    # ------------------------------------------------------
    # Behavioral / Intent Score
    #
    # Measures lead engagement and buying intent.
    #
    # Examples:
    # - Email opens
    # - Website activity
    # - Meetings attended
    # - Recent interactions
    # ------------------------------------------------------
    behavior_score: float

    # ------------------------------------------------------
    # Data Quality Score
    #
    # Measures reliability and trustworthiness
    # of lead data.
    #
    # Examples:
    # - Valid business email
    # - Real phone number
    # - Non-spam lead
    # ------------------------------------------------------
    quality_score: float

    # ------------------------------------------------------
    # Penalty / Risk Score
    #
    # Deducts points for suspicious,
    # incomplete, or low-quality signals.
    #
    # Examples:
    # - Fake/test emails
    # - Spam patterns
    # - Missing critical fields
    # ------------------------------------------------------
    penalty_score: float

    # ------------------------------------------------------
    # Final aggregated lead score
    #
    # Usually computed using weighted logic
    # across all scoring layers.
    # ------------------------------------------------------
    total_score: float

    # ------------------------------------------------------
    # Human-readable lead classification
    #
    # Examples:
    # - "Hot"
    # - "Warm"
    # - "Cold"
    # - "High Intent"
    # ------------------------------------------------------
    classification: str

    # ------------------------------------------------------
    # Confidence score
    #
    # Represents how reliable/confident
    # the scoring engine is about this result.
    #
    # Higher confidence usually means:
    # - More complete data
    # - Stronger signals
    # - Better ML certainty
    # ------------------------------------------------------
    confidence: float

    # ------------------------------------------------------
    # Explainability reasons
    #
    # Stores structured explanations for why
    # the lead received its score.
    #
    # Example:
    # [
    #   {
    #       "signal": "business_email",
    #       "impact": "+20",
    #       "reason": "Corporate email detected"
    #   }
    # ]
    #
    # Useful for:
    # - AI summaries
    # - UI explanations
    # - Audit/debugging
    # ------------------------------------------------------
    reasons: List[Dict]