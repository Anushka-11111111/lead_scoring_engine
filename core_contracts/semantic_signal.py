from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SemanticSignal:
    """
    Represents the CORE intelligence unit of the lead scoring system.

    This is one of the most important architectural objects
    in the entire pipeline.

    Purpose:
    Converts low-level raw CRM observations into
    semantically meaningful business signals.

    Example Transformation:
    Raw CRM Field:
        "sf_email": "john@company.com"

    Semantic Interpretation:
        signal_type = "identity"
        signal_strength = 0.92
        signal_weight = 10

    Why this matters:
    Raw CRM data alone has no business meaning.
    SemanticSignal adds:
    - Context
    - Classification
    - Confidence
    - Importance weighting

    This allows downstream systems to reason about
    lead quality and intent intelligently.
    """

    # ------------------------------------------------------
    # Unique lead identifier
    #
    # Associates this signal with a CRM lead.
    # ------------------------------------------------------
    lead_id: str

    # ------------------------------------------------------
    # Unique signal identifier
    #
    # Useful for:
    # - Tracking signals
    # - Deduplication
    # - Debugging
    # - Observability
    # ------------------------------------------------------
    signal_id: str

    # ------------------------------------------------------
    # Original CRM field path
    #
    # Example:
    # "sf_email"
    # "sf_pipeline_stage.winprobability"
    #
    # Preserves traceability back to the source field.
    # ------------------------------------------------------
    field_path: str

    # ------------------------------------------------------
    # Actual signal value extracted from CRM
    #
    # Examples:
    # "john@company.com"
    # 85
    # "USA"
    # True
    # ------------------------------------------------------
    value: Any

    # ------------------------------------------------------
    # High-level semantic classification
    #
    # Common types:
    # - fit
    # - behavior
    # - quality
    # - unknown
    #
    # This enables:
    # - Category-based scoring
    # - Rule grouping
    # - ML feature engineering
    # ------------------------------------------------------
    signal_type: str

    # ------------------------------------------------------
    # Confidence score of semantic classification
    #
    # Range:
    # 0.0 → low confidence
    # 1.0 → extremely confident
    #
    # Example:
    # A valid business email may produce:
    # signal_strength = 0.95
    #
    # Used for:
    # - Confidence estimation
    # - AI explainability
    # - Weighted scoring
    # ------------------------------------------------------
    signal_strength: float

    # ------------------------------------------------------
    # Relative importance of this signal
    #
    # Higher weight means:
    # - Greater scoring impact
    # - Higher business importance
    #
    # Example:
    # Pipeline probability → high weight
    # City field → lower weight
    # ------------------------------------------------------
    signal_weight: float

    # ------------------------------------------------------
    # Additional signal metadata
    #
    # Flexible extension layer for storing:
    # - Validation info
    # - Quality metrics
    # - Source mappings
    # - Rule annotations
    # - ML feature metadata
    #
    # Example:
    # {
    #     "quality_score": 92,
    #     "normalized": True
    # }
    # ------------------------------------------------------
    metadata: Dict = field(default_factory=dict)