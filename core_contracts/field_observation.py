from dataclasses import dataclass
from typing import Any


@dataclass
class FieldObservation:
    """
    Represents a SINGLE flattened field extracted from CRM data.

    This is a pure data container (DTO / schema object).
    It intentionally contains:
    - No scoring logic
    - No business intelligence
    - No transformation behavior

    Purpose:
    Standardizes how individual CRM fields are represented
    throughout the pipeline.

    Example:
    CRM Input:
    {
        "contact": {
            "email": "john@company.com"
        }
    }

    Flattened Observation:
    FieldObservation(
        lead_id="123",
        path="contact.email",
        value="john@company.com",
        value_type="str",
        depth=2,
        is_null=False,
        source_path="contact.email"
    )

    Why this structure matters:
    - Creates consistency across the pipeline
    - Easier debugging/logging
    - Cleaner ML feature generation
    - Better explainability
    - Simplifies rule engine processing
    """

    # ------------------------------------------------------
    # Unique lead identifier
    # Used to associate this field with a CRM lead
    # ------------------------------------------------------
    lead_id: str

    # ------------------------------------------------------
    # Flattened field path
    #
    # Example:
    # "contact.email"
    # "company.employee_count"
    # ------------------------------------------------------
    path: str

    # ------------------------------------------------------
    # Actual field value extracted from CRM
    #
    # Can be:
    # - string
    # - int
    # - float
    # - bool
    # - etc.
    # ------------------------------------------------------
    value: Any

    # ------------------------------------------------------
    # Data type of the field value
    #
    # Examples:
    # "str"
    # "int"
    # "bool"
    # ------------------------------------------------------
    value_type: str

    # ------------------------------------------------------
    # Nesting depth inside original CRM JSON
    #
    # Example:
    # contact.email → depth 2
    # ------------------------------------------------------
    depth: int

    # ------------------------------------------------------
    # Indicates whether original value was null/empty
    #
    # Useful for:
    # - Missing data analysis
    # - Data quality checks
    # - ML missing-feature handling
    # ------------------------------------------------------
    is_null: bool

    # ------------------------------------------------------
    # Original CRM reference path
    #
    # Usually same as flattened path,
    # but preserved separately for traceability/debugging.
    # ------------------------------------------------------
    source_path: str