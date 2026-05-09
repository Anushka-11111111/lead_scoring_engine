from dataclasses import dataclass
from typing import List


@dataclass
class RuleMatch:
    """
    Represents the result of evaluating ONE rule
    inside the rule engine.

    Each RuleMatch object captures:
    - Whether the rule triggered
    - Which signals were involved
    - Score impact
    - Business category
    - Human-readable explanation
    - Confidence level

    Purpose:
    - Provides explainable scoring
    - Enables auditability/debugging
    - Supports AI-generated summaries
    - Tracks rule-level scoring contributions

    Example:
    A rule may detect:
    - Business email present
    - Recent CRM activity
    - High pipeline probability

    If triggered, the rule produces a RuleMatch
    describing the impact.
    """

    # ------------------------------------------------------
    # Unique rule identifier
    #
    # Example:
    # "RULE_BUSINESS_EMAIL"
    # "RULE_HIGH_INTENT_ACTIVITY"
    # ------------------------------------------------------
    rule_id: str

    # ------------------------------------------------------
    # Indicates whether the rule successfully matched
    #
    # True  → rule conditions satisfied
    # False → rule conditions not satisfied
    # ------------------------------------------------------
    triggered: bool

    # ------------------------------------------------------
    # List of CRM fields/signals involved
    # in triggering this rule
    #
    # Example:
    # [
    #   "sf_email",
    #   "sf_pipeline_stage.winprobability"
    # ]
    #
    # Useful for:
    # - Explainability
    # - Auditing
    # - Debugging
    # ------------------------------------------------------
    impacted_signals: List[str]

    # ------------------------------------------------------
    # Numerical score impact produced by this rule
    #
    # Positive values:
    # + boost lead score
    #
    # Negative values:
    # - apply penalties/risk deductions
    #
    # Example:
    # +20 → strong positive signal
    # -15 → suspicious/fake behavior
    # ------------------------------------------------------
    score_delta: float

    # ------------------------------------------------------
    # High-level scoring category
    #
    # Common categories:
    # - fit
    # - behavior
    # - quality
    # - penalty
    #
    # Helps aggregate scoring dimensions.
    # ------------------------------------------------------
    category: str

    # ------------------------------------------------------
    # Human-readable explanation of why
    # the rule triggered.
    #
    # Example:
    # "Business email detected"
    # "Recent lead activity found"
    # "Fake/test email identified"
    #
    # Used for:
    # - Explainable AI
    # - UI tooltips
    # - Sales transparency
    # ------------------------------------------------------
    reason: str

    # ------------------------------------------------------
    # Confidence level of this rule evaluation
    #
    # Represents how reliable/certain
    # this rule outcome is.
    #
    # Higher confidence usually means:
    # - Stronger signal quality
    # - Better data completeness
    # - Clear rule match conditions
    # ------------------------------------------------------
    confidence: float