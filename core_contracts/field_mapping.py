# ==========================================================
# FIELD MAPPING CONFIGURATION
# ==========================================================
#
# Purpose:
# This configuration acts as the central metadata registry
# for all CRM fields used inside the lead scoring system.
#
# It standardizes:
# - Signal classification
# - Feature categorization
# - Signal importance/weighting
#
# Why this layer matters:
# Instead of hardcoding logic everywhere, the system can
# dynamically understand:
#
#   "What kind of signal is this?"
#   "How important is it?"
#   "Which business category does it belong to?"
#
# This makes the scoring engine:
# - Modular
# - Config-driven
# - Easier to scale
# - Easier to maintain
#
# Example:
# "sf_email" →
#     identity signal
#     email signal type
#     weight = 10
#
# The scoring engine can later use this metadata to:
# - Assign scores
# - Generate explanations
# - Build ML features
# - Trigger rules dynamically
# ==========================================================

FIELD_MAPPING = {

    # ======================================================
    # 🪪 IDENTITY SIGNALS
    # ======================================================
    # Signals used to identify or validate a lead.
    # These are foundational trust signals.
    # ======================================================

    "sf_email": {

        # Internal signal classification
        "signal_type": "email_signal",

        # High-level business category
        "category": "identity",

        # Relative importance in scoring
        "weight": 10
    },

    "sf_phone_number.value": {

        "signal_type": "phone_signal",

        "category": "identity",

        "weight": 10
    },

    # ======================================================
    # ⏳ TEMPORAL SIGNALS
    # ======================================================
    # Signals related to timing and recency.
    #
    # These help determine:
    # - Lead freshness
    # - Engagement recency
    # - Active buying intent
    # ======================================================

    "sf_created_at": {

        # When the lead was originally created
        "signal_type": "lead_recency_signal",

        "category": "temporal",

        "weight": 15
    },

    "sf_latest_activity_on": {

        # Most recent interaction/activity timestamp
        "signal_type": "activity_recency_signal",

        "category": "temporal",

        # Higher importance because recent activity
        # is usually a strong intent signal
        "weight": 20
    },

    # ======================================================
    # 📈 PIPELINE / INTENT SIGNALS
    # ======================================================
    # Signals representing sales pipeline quality,
    # buying intent, or conversion likelihood.
    # ======================================================

    "sf_pipeline_stage.winprobability": {

        # CRM-estimated conversion probability
        "signal_type": "conversion_probability_signal",

        "category": "intent",

        # High weight because this is often one of
        # the strongest indicators of conversion intent
        "weight": 25
    },

    # ======================================================
    # 📣 SOURCE / MARKETING SIGNALS
    # ======================================================
    # Acquisition channel signals.
    #
    # Useful for:
    # - Attribution analysis
    # - Marketing quality analysis
    # - Campaign optimization
    # ======================================================

    "sf_source.label": {

        "signal_type": "acquisition_channel_signal",

        "category": "marketing",

        "weight": 10
    },

    "cf_lead_source.label": {

        "signal_type": "acquisition_channel_signal",

        "category": "marketing",

        "weight": 10
    },

    # ======================================================
    # 🌍 LOCATION / DEMOGRAPHIC SIGNALS
    # ======================================================
    # Geographic enrichment signals.
    #
    # Useful for:
    # - Territory routing
    # - ICP matching
    # - Geo-based prioritization
    # ======================================================

    "sf_city": {

        "signal_type": "location_signal",

        "category": "demographic",

        # Lower weight because location alone
        # is usually not a strong conversion signal
        "weight": 5
    },

    "sf_state": {

        "signal_type": "location_signal",

        "category": "demographic",

        "weight": 5
    }
}