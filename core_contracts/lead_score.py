from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class LeadScore:
    """
    Represents the FINAL lead scoring result produced
    by the scoring engine.

    This object acts as the standardized response model
    for the entire lead scoring pipeline.

    It combines multiple scoring dimensions into a single,
    explainable business outcome.

    Main Responsibilities:
    - Store all scoring components
    - Store final classification
    - Provide explainability metadata
    - Track signal coverage/completeness

    This object is typically:
    - Returned by APIs
    - Stored in databases
    - Sent to CRMs/frontends
    - Consumed by AI explanation layers
    """

    # ------------------------------------------------------
    # Unique CRM lead identifier
    # ------------------------------------------------------
    lead_id: str

    # ------------------------------------------------------
    # ICP / Fit Score
    #
    # Measures how closely the lead matches
    # the Ideal Customer Profile.
    #
    # Example factors:
    # - Industry
    # - Company size
    # - Geography
    # - Job role
    # ------------------------------------------------------
    fit_score: float

    # ------------------------------------------------------
    # Behavioral / Intent Score
    #
    # Measures user engagement and buying signals.
    #
    # Example factors:
    # - Website activity
    # - Email opens
    # - Meetings attended
    # - CRM interactions
    # ------------------------------------------------------
    behavior_score: float

    # ------------------------------------------------------
    # Data Quality Score
    #
    # Measures reliability and completeness
    # of lead information.
    #
    # Example factors:
    # - Valid email
    # - Valid phone
    # - Fresh lead
    # ------------------------------------------------------
    quality_score: float

    # ------------------------------------------------------
    # Penalty / Risk Score
    #
    # Negative scoring component used to reduce
    # score for suspicious or low-quality leads.
    #
    # Example penalties:
    # - Fake/test emails
    # - Spam phone numbers
    # - Missing critical fields
    # ------------------------------------------------------
    penalty_score: float

    # ------------------------------------------------------
    # Final aggregated lead score
    #
    # Usually derived from:
    # fit + behavior + quality - penalties
    # ------------------------------------------------------
    total_score: float

    # ------------------------------------------------------
    # Final lead category
    #
    # Common categories:
    # - hot
    # - warm
    # - cold
    #
    # Used for:
    # - Sales prioritization
    # - Lead routing
    # - CRM visualization
    # ------------------------------------------------------
    classification: str

    # ------------------------------------------------------
    # Confidence score
    #
    # Indicates how trustworthy or reliable
    # the scoring result is.
    #
    # Higher confidence generally means:
    # - Better data coverage
    # - Stronger signals
    # - Higher ML certainty
    # ------------------------------------------------------
    confidence: float

    # ------------------------------------------------------
    # Human-readable explanations
    #
    # Stores textual explanations describing
    # why the lead received its score.
    #
    # Example:
    # [
    #   "Business email detected",
    #   "Recent activity found",
    #   "High win probability"
    # ]
    #
    # Used for:
    # - Explainable AI
    # - UI tooltips
    # - Debugging
    # ------------------------------------------------------
    explanations: List[str] = field(default_factory=list)

    # ------------------------------------------------------
    # Signal coverage metadata
    #
    # Tracks how much useful signal data
    # was available during scoring.
    #
    # Example:
    # {
    #   "identity": 80,
    #   "behavior": 60,
    #   "intent": 90
    # }
    #
    # Useful for:
    # - Confidence estimation
    # - Data completeness analysis
    # - ML observability
    # ------------------------------------------------------
    signal_coverage: Dict = field(default_factory=dict)