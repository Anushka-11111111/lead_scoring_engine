from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Condition:
    """
    Represents ONE logical condition inside a rule.

    Purpose:
    Conditions define the actual matching logic
    used by the rule engine.

    A condition evaluates:
        signal field
            +
        operator
            +
        target value

    Example:
        field     = "sf_country"
        operator  = "eq"
        value     = "usa"

    Meaning:
        sf_country == "usa"

    Supported Operators:
    - eq
    - neq
    - gt
    - lt
    - gte
    - lte
    - contains
    - regex
    - exists
    - missing
    - valid_email
    - valid_phone
    """

    # --------------------------------------------------
    # CRM/signal field to evaluate
    #
    # Examples:
    # - signal_type
    # - value
    # - field_path
    # - sf_country
    # --------------------------------------------------
    field: str

    # --------------------------------------------------
    # Comparison operator
    #
    # Examples:
    # - eq
    # - gt
    # - contains
    # - regex
    # --------------------------------------------------
    operator: str

    # --------------------------------------------------
    # Target comparison value
    #
    # Examples:
    # - "usa"
    # - 50
    # - ["india", "usa"]
    # --------------------------------------------------
    value: Any


@dataclass
class Rule:
    """
    Represents ONE business scoring rule.

    Purpose:
    Rules define business intelligence logic
    used for lead scoring.

    A rule contains:
    - Metadata
    - Scoring information
    - Conditions
    - Logical evaluation strategy

    Example:
        Rule:
            "High Pipeline Probability"

        Conditions:
            win_probability >= 80

        Outcome:
            Increase lead behavior score

    Why rules matter:
    Rules provide:
    - Explainable AI
    - Deterministic scoring
    - Business control
    - Custom scoring logic
    - Domain intelligence
    """

    # --------------------------------------------------
    # Unique rule identifier
    #
    # Example:
    # "RULE_001"
    # --------------------------------------------------
    rule_id: str

    # --------------------------------------------------
    # Human-readable rule name
    #
    # Example:
    # "High Pipeline Probability"
    # --------------------------------------------------
    name: str

    # --------------------------------------------------
    # Scoring category
    #
    # Determines which score bucket
    # this rule contributes to.
    #
    # Supported:
    # - fit
    # - behavior
    # - quality
    # - penalty
    # --------------------------------------------------
    category: str

    # --------------------------------------------------
    # Base/static rule score
    #
    # NOTE:
    # May later be dynamically adjusted
    # by RuleExecutor.
    # --------------------------------------------------
    score: float

    # --------------------------------------------------
    # List of rule conditions
    #
    # ALL/ANY of these conditions
    # are evaluated depending on logic mode.
    # --------------------------------------------------
    conditions: List[Condition]

    # --------------------------------------------------
    # Logical evaluation mode
    #
    # Supported:
    # - AND → all conditions required
    # - OR  → any condition required
    #
    # Default:
    # AND
    # --------------------------------------------------
    logic: str = "AND"

    # --------------------------------------------------
    # Optional human-readable explanation
    #
    # Useful for:
    # - dashboards
    # - explainability
    # - debugging
    # - sales visibility
    # --------------------------------------------------
    description: str = ""