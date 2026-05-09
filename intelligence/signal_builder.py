import uuid
from typing import List, Union, Dict, Any
import re

from core_contracts.semantic_signal import SemanticSignal
from intelligence.signal_weighting import SignalWeighter
from core_contracts.field_mapping import FIELD_MAPPING


def normalize_field_path(path: str) -> str:
    """
    Normalizes CRM field paths into a consistent format.

    Why normalization matters:
    CRM systems often produce inconsistent field paths.

    Example variations:
        sf_email
        SF_Email
        contacts[0].email
        contacts[1].email

    Without normalization:
    - Field mapping becomes unreliable
    - Rule matching breaks
    - Duplicate semantic signals appear

    This function standardizes paths by:
    - Converting to lowercase
    - Removing array indexes

    Example:
        contacts[0].email
        → contacts.email
    """

    # Remove surrounding whitespace
    path = path.strip().lower()

    # Remove array indexes:
    # [0], [1], [25], etc.
    path = re.sub(r"\[\d+\]", "", path)

    return path


class SignalBuilder:
    """
    Converts raw CRM observations into SemanticSignal objects.

    This is a CORE intelligence transformation layer.

    Responsibilities:
    - Normalize CRM fields
    - Match fields to semantic mappings
    - Inject signal intelligence
    - Apply quality-aware weighting
    - Generate standardized semantic signals

    Pipeline Flow:
        Raw CRM Fields
            ↓
        Field Normalization
            ↓
        Mapping Resolution
            ↓
        Weight Calculation
            ↓
        Quality Injection
            ↓
        SemanticSignal Generation

    Why this layer matters:
    Raw CRM fields are not meaningful by themselves.

    SignalBuilder transforms them into:
    - Structured intelligence
    - ML-friendly features
    - Rule-engine-compatible signals
    - Explainable scoring inputs
    """

    def __init__(self):
        """
        Initializes signal builder dependencies.
        """

        # Signal weighting engine
        #
        # Responsible for calculating dynamic
        # rule/business importance weights.
        self.weighter = SignalWeighter()

    def build(
        self,
        observations: Union[List[Any], Dict],
        quality_map: Dict[str, float] = None
    ) -> List[SemanticSignal]:
        """
        Converts CRM observations into semantic signals.

        Args:
            observations:
                Either:
                - Flattened observation dictionary
                - List of FieldObservation objects

            quality_map:
                Optional feature quality scores generated
                by FeatureQualityLayer.

                Example:
                {
                    "sf_email": 95,
                    "sf_phone_number.value": 80
                }

        Returns:
            List[SemanticSignal]:
                Final normalized semantic signals.
        """

        # Final semantic signal output
        signals = []

        # Fallback empty quality map
        quality_map = quality_map or {}

        # --------------------------------------------------
        # Normalize input structure
        # --------------------------------------------------
        #
        # Supports:
        # 1. Dictionary input
        # 2. List of observation objects
        #
        # This makes the builder flexible across
        # multiple pipeline stages.
        # --------------------------------------------------

        if isinstance(observations, dict):

            # Convert dictionary into iterable key/value pairs
            items = observations.items()

            # Extract lead ID if available
            lead_id = observations.get("sf_id", "unknown")

        else:

            # Convert observation objects into tuples
            items = [(obs.path, obs.value) for obs in observations]

            # Safely extract lead ID
            lead_id = (
                getattr(observations[0], "lead_id", "unknown")
                if observations else "unknown"
            )

        # --------------------------------------------------
        # Build semantic signals
        # --------------------------------------------------
        for path, value in items:

            # --------------------------------------------------
            # Skip empty/junk values
            # --------------------------------------------------
            if value is None or value == "":
                continue

            # Normalize CRM field path
            norm_path = normalize_field_path(path)

            # --------------------------------------------------
            # Explicit field mapping lookup
            #
            # IMPORTANT:
            # Only explicitly mapped fields become
            # semantic signals.
            #
            # This prevents noisy/untrusted fields
            # from entering scoring logic.
            # --------------------------------------------------
            field_config = FIELD_MAPPING.get(norm_path)

            # Ignore unknown/unmapped fields
            if not field_config:
                continue

            # Extract semantic signal type
            signal_type = field_config["signal_type"]

            # Base importance weight from mapping config
            base_weight = field_config["weight"]

            # --------------------------------------------------
            # 🧠 QUALITY INJECTION
            # --------------------------------------------------
            #
            # This is a CRITICAL architectural improvement.
            #
            # Instead of treating all fields equally,
            # signal contribution becomes quality-aware.
            #
            # Example:
            # High-quality business email
            # → stronger scoring impact
            #
            # Fake/test email
            # → lower scoring impact
            # --------------------------------------------------

            # Retrieve feature quality score
            #
            # Default = 1.0 (fully trusted)
            quality_score = quality_map.get(norm_path, 1.0)

            # --------------------------------------------------
            # Dynamic rule/business weighting
            # --------------------------------------------------
            #
            # Uses signal-specific logic
            # to compute contextual importance.
            # --------------------------------------------------
            rule_weight = self.weighter.get_weight(
                signal_type,
                value
            )

            # --------------------------------------------------
            # FINAL ENRICHED SIGNAL WEIGHT
            # --------------------------------------------------
            #
            # Core intelligence formula:
            #
            # Final Weight =
            #     Rule Importance
            #     ×
            #     Signal Quality
            #
            # This makes scoring:
            # - Smarter
            # - More reliable
            # - Quality-aware
            # --------------------------------------------------
            final_weight = rule_weight * quality_score

            # --------------------------------------------------
            # Create semantic signal object
            # --------------------------------------------------
            signals.append(

                SemanticSignal(

                    # Lead ownership
                    lead_id=lead_id,

                    # Unique signal tracking ID
                    signal_id=str(uuid.uuid4()),

                    # Normalized CRM field path
                    field_path=norm_path,

                    # Original field value
                    value=value,

                    # Semantic classification
                    signal_type=signal_type,

                    # Base semantic importance
                    #
                    # Represents intrinsic feature importance
                    signal_strength=base_weight,

                    # Final quality-aware contribution
                    signal_weight=final_weight,

                    # Additional signal metadata
                    metadata={

                        # Signal generation strategy
                        "source": "explicit_mapping_with_quality",

                        # Original Python data type
                        "value_type": type(value).__name__,

                        # Injected feature quality score
                        "quality_score": quality_score
                    }
                )
            )

        return signals