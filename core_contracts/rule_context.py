from dataclasses import dataclass, field
from typing import List, Dict

from core_contracts.semantic_signal import SemanticSignal


@dataclass
class RuleContext:
    """
    Represents the fully normalized input passed into
    the rule engine.

    This is one of the most important internal contracts
    in the scoring architecture.

    Purpose:
    - Provides a clean, structured view of lead signals
    - Removes dependency on raw CRM payloads
    - Enables fast rule evaluation
    - Supports semantic indexing/lookups

    Design Philosophy:
    By the time data reaches RuleContext:
    - Raw CRM complexity is already removed
    - Signals are normalized and standardized
    - The rule engine can operate safely and consistently

    This ensures:
    - Cleaner rule logic
    - Faster matching
    - Better scalability
    - Easier debugging
    """

    # ------------------------------------------------------
    # Unique lead identifier
    #
    # Used to associate this rule context
    # with a specific CRM lead.
    # ------------------------------------------------------
    lead_id: str

    # ------------------------------------------------------
    # Fully normalized semantic signals
    #
    # Each signal represents a structured,
    # semantically meaningful CRM observation.
    #
    # Example:
    # SemanticSignal(
    #     signal_type="email_signal",
    #     path="sf_email",
    #     value="john@company.com"
    # )
    #
    # These signals are the primary inputs
    # evaluated by the rule engine.
    # ------------------------------------------------------
    signals: List[SemanticSignal]

    # ------------------------------------------------------
    # Fast lookup index grouped by signal type
    #
    # Example:
    # {
    #     "email_signal": [...],
    #     "location_signal": [...]
    # }
    #
    # Purpose:
    # Allows rules to quickly fetch signals
    # by semantic category/type.
    #
    # Improves:
    # - Performance
    # - Rule readability
    # - Query efficiency
    # ------------------------------------------------------
    index_by_type: Dict[str, List[SemanticSignal]] = field(default_factory=dict)

    # ------------------------------------------------------
    # Fast lookup index grouped by signal path
    #
    # Example:
    # {
    #     "sf_email": SemanticSignal(...),
    #     "sf_country": SemanticSignal(...)
    # }
    #
    # Purpose:
    # Enables O(1)-style direct field access
    # during rule evaluation.
    # ------------------------------------------------------
    index_by_path: Dict[str, SemanticSignal] = field(default_factory=dict)

    # ------------------------------------------------------
    # Total number of extracted signals
    #
    # Includes:
    # - Known signals
    # - Unknown/unmapped signals
    # ------------------------------------------------------
    total_signals: int = 0

    # ------------------------------------------------------
    # Number of recognized/normalized signals
    #
    # Known signals are fields that:
    # - Exist in field mapping registry
    # - Are semantically understood
    # - Can participate in scoring
    # ------------------------------------------------------
    known_signals: int = 0

    # ------------------------------------------------------
    # Number of unknown/unmapped signals
    #
    # Unknown signals are fields that:
    # - Do not exist in mapping registry
    # - Are unsupported
    # - Are not yet modeled
    #
    # Useful for:
    # - Observability
    # - Schema evolution
    # - CRM integration debugging
    # ------------------------------------------------------
    unknown_signals: int = 0