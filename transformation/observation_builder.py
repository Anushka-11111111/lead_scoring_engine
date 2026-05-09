from typing import List, Any

from core_contracts.field_observation import FieldObservation
from transformation.flattener import CRMFlattener


class ObservationBuilder:
    """
    Observation generation layer.

    Purpose:
    Converts raw CRM payloads into structured
    FieldObservation objects.

    Pipeline Role:
        Raw CRM JSON
              ↓
        CRMFlattener
              ↓
        Flat field tuples
              ↓
        ObservationBuilder
              ↓
        FieldObservation objects

    Why this layer exists:
    Raw CRM payloads are:
    - inconsistent
    - deeply nested
    - difficult to analyze directly

    FieldObservation provides:
    - standardized structure
    - metadata
    - typing
    - depth information
    - null detection

    This becomes the foundation for:
    - signal extraction
    - rule evaluation
    - ML feature engineering
    - analytics
    """

    def __init__(self):
        """
        Initializes observation builder.

        Creates reusable CRM flattener instance.
        """

        # Universal nested JSON flattener
        self.flattener = CRMFlattener()

    # ==================================================
    # MAIN OBSERVATION BUILDER
    # ==================================================
    def build(
        self,
        lead_id: str,
        crm_payload: Any
    ) -> List[FieldObservation]:
        """
        Converts CRM payload into FieldObservation objects.

        Args:
            lead_id:
                Unique CRM lead identifier

            crm_payload:
                Raw CRM JSON payload

        Returns:
            List of structured FieldObservation objects
        """

        # --------------------------------------------------
        # Step 1:
        # Flatten nested CRM structure
        #
        # Example:
        # contact.email → value
        # --------------------------------------------------
        flattened = self.flattener.flatten(
            crm_payload
        )

        # Final structured observations
        observations: List[
            FieldObservation
        ] = []

        # ==================================================
        # BUILD OBSERVATIONS
        # ==================================================
        for path, value, depth in flattened:

            # --------------------------------------------------
            # Create structured observation object
            # --------------------------------------------------
            obs = FieldObservation(

                # Parent lead ID
                lead_id=lead_id,

                # Flattened field path
                #
                # Example:
                # contact.email
                #
                # Fallback:
                # "root"
                path=path if path else "root",

                # Actual field value
                value=value,

                # Auto-detected type
                #
                # Examples:
                # str
                # int
                # bool
                # list
                value_type=self._get_type(value),

                # Nesting depth
                #
                # Useful for:
                # - analytics
                # - debugging
                # - complexity analysis
                depth=depth,

                # Null-state tracking
                is_null=value is None,

                # Original source reference
                #
                # Helps preserve traceability
                source_path=(
                    path if path else "root"
                ),
            )

            # Store observation
            observations.append(obs)

        return observations

    # ==================================================
    # TYPE DETECTION HELPER
    # ==================================================
    def _get_type(self, value: Any) -> str:
        """
        Safely determines value datatype.

        Why needed:
        CRM systems often contain:
        - mixed schemas
        - inconsistent typing
        - null-heavy payloads

        Returns:
            String representation of type
        """

        # Explicit null handling
        if value is None:
            return "null"

        # Examples:
        # str
        # int
        # float
        # bool
        # dict
        return type(value).__name__