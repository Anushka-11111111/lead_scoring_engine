from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RawCRMInput:
    """
    Represents the RAW entry point into the lead scoring system.

    This object is designed to accept CRM payloads exactly
    as they arrive from external systems, with minimal assumptions.

    Key Design Principle:
    The system should remain CRM-agnostic.

    Meaning:
    - Different CRMs may send different schemas
    - Payload structures may vary significantly
    - Nested fields may differ across integrations

    This layer simply standardizes:
    - Lead identity
    - Source metadata
    - Raw payload container

    No business logic or transformation happens here.
    """

    # ------------------------------------------------------
    # Unique lead identifier
    #
    # Used throughout the pipeline to:
    # - Track lead processing
    # - Associate scores
    # - Link observations/features
    # ------------------------------------------------------
    lead_id: str

    # ------------------------------------------------------
    # Source CRM/system name
    #
    # Examples:
    # - Salesforce
    # - HubSpot
    # - Zoho
    # - Custom API
    #
    # Useful for:
    # - Multi-CRM support
    # - Source-specific debugging
    # - Integration analytics
    # ------------------------------------------------------
    source: str

    # ------------------------------------------------------
    # Timestamp of payload ingestion or event creation
    #
    # Useful for:
    # - Event ordering
    # - Processing history
    # - Time-series analytics
    # - Recency calculations
    # ------------------------------------------------------
    timestamp: str

    # ------------------------------------------------------
    # Raw CRM payload
    #
    # Stores the FULL original CRM data exactly
    # as received from the external system.
    #
    # The payload may contain:
    # - Nested dictionaries
    # - Lists/arrays
    # - CRM-specific custom fields
    # - Dynamic schemas
    #
    # Example:
    # {
    #     "contact": {
    #         "email": "john@company.com"
    #     },
    #     "company": {
    #         "size": 200
    #     }
    # }
    #
    # This raw payload is later processed by:
    # - Field extractors
    # - Signal mappers
    # - Feature engineering layers
    # ------------------------------------------------------
    payload: Dict[str, Any]