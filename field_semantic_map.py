```python id="fsm920"
# ==========================================================
# field_semantic_map.py
# ==========================================================
#
# FIELD → SEMANTIC INTELLIGENCE MAP
#
# Purpose:
# Maps raw CRM field paths into:
# - semantic meaning
# - signal category
# - confidence score
#
# This is the SINGLE SOURCE OF TRUTH
# for interpreting CRM fields.
#
# ==========================================================
#
# Why this layer exists:
#
# CRM systems are inconsistent.
#
# Different CRMs may represent the same concept as:
#
#     email
#     sf_email
#     contact.email
#     lead.email
#
# This mapping layer standardizes meaning.
#
# ==========================================================
#
# Output Structure:
#
#     field_path: (
#         signal_type,
#         confidence_score
#     )
#
# Example:
#
#     "sf_email": ("fit", 0.95)
#
# Means:
# - This field represents a FIT signal
# - Confidence in interpretation = 95%
#
# ==========================================================
#
# Signal Categories:
#
# FIT
# ----
# Who the lead is.
#
# Examples:
# - email
# - company
# - owner
# - pipeline stage
#
#
# BEHAVIOR
# --------
# What the lead is doing.
#
# Examples:
# - recent activity
# - pipeline probability
# - source channel
#
#
# QUALITY
# -------
# How complete/trustworthy the data is.
#
# Examples:
# - address
# - zipcode
# - country
# - phone
#
# ==========================================================
#
# IMPORTANT:
# This architecture is intentionally static today,
# but future versions can replace this with:
#
# - ML semantic inference
# - embedding similarity
# - ontology mapping
# - vector search
# - LLM interpretation
#
# ==========================================================

FIELD_SEMANTIC_MAP = {

    # ======================================================
    # FIT SIGNALS
    # ======================================================
    #
    # Represents:
    # "Who the lead is"
    #
    # Used for:
    # - qualification
    # - account matching
    # - ICP scoring
    # - ownership analysis
    #
    # ======================================================

    # ------------------------------------------------------
    # Email identity
    #
    # High-confidence fit signal because:
    # email strongly identifies a lead.
    # ------------------------------------------------------
    "sf_email": ("fit", 0.95),

    "email": ("fit", 0.95),

    # ------------------------------------------------------
    # Phone identity
    # ------------------------------------------------------
    "sf_phone_number": ("fit", 0.90),

    "phone": ("fit", 0.90),

    # ------------------------------------------------------
    # CRM ownership
    #
    # Indicates:
    # - sales assignment
    # - account responsibility
    # - lead routing
    # ------------------------------------------------------
    "sf_owner": ("fit", 0.70),

    "sf_past_owner": ("fit", 0.65),

    # ------------------------------------------------------
    # CRM tags
    #
    # Often indicate:
    # - segmentation
    # - campaign labels
    # - business categories
    # ------------------------------------------------------
    "sf_tag.name": ("fit", 0.80),

    "sf_tag.label": ("fit", 0.80),

    # ------------------------------------------------------
    # Pipeline stage
    #
    # Important for:
    # - qualification stage
    # - sales readiness
    # - funnel positioning
    # ------------------------------------------------------
    "sf_pipeline_stage.name": ("fit", 0.85),

    "sf_pipeline_stage.label": ("fit", 0.85),

    # ------------------------------------------------------
    # Lead status
    # ------------------------------------------------------
    "sf_status.label": ("fit", 0.75),

    "sf_status.value": ("fit", 0.70),

    # ======================================================
    # INTENT / BEHAVIOR SIGNALS
    # ======================================================
    #
    # Represents:
    # "What the lead is doing"
    #
    # Used for:
    # - engagement analysis
    # - buying intent
    # - conversion likelihood
    # - activity tracking
    #
    # ======================================================

    # ------------------------------------------------------
    # Pipeline win probability
    #
    # Extremely strong buying-intent signal.
    # ------------------------------------------------------
    "sf_pipeline_stage.winProbability":
        ("behavior", 0.90),

    # ------------------------------------------------------
    # Latest CRM activity
    #
    # Indicates:
    # - engagement freshness
    # - sales interaction
    # - activity recency
    # ------------------------------------------------------
    "sf_latest_activity_on":
        ("behavior", 0.85),

    # ------------------------------------------------------
    # Assignment date
    #
    # Indicates:
    # - sales workflow movement
    # - active ownership
    # ------------------------------------------------------
    "sf_assigned_date":
        ("behavior", 0.80),

    # ------------------------------------------------------
    # Lead acquisition source
    #
    # Important for:
    # - marketing attribution
    # - campaign quality
    # - conversion trends
    # ------------------------------------------------------
    "sf_source.label":
        ("behavior", 0.70),

    "sf_source.value":
        ("behavior", 0.70),

    # ------------------------------------------------------
    # Custom lead source fields
    # ------------------------------------------------------
    "cf_lead_source.label":
        ("behavior", 0.65),

    "cf_lead_source.value":
        ("behavior", 0.65),

    # ------------------------------------------------------
    # Update source type
    #
    # Example:
    # manual update
    # API update
    # automation update
    # ------------------------------------------------------
    "sf_updated_via_type.label":
        ("behavior", 0.60),

    # ======================================================
    # QUALITY SIGNALS
    # ======================================================
    #
    # Represents:
    # "How complete/trustworthy the lead data is"
    #
    # Used for:
    # - data hygiene scoring
    # - enrichment quality
    # - completeness analysis
    #
    # ======================================================

    # ------------------------------------------------------
    # Postal code
    # ------------------------------------------------------
    "sf_zipcode":
        ("quality", 0.70),

    # ------------------------------------------------------
    # Geographic enrichment
    # ------------------------------------------------------
    "sf_city":
        ("quality", 0.65),

    "sf_state":
        ("quality", 0.65),

    "sf_country":
        ("quality", 0.65),

    # ------------------------------------------------------
    # Nested address structures
    #
    # Useful for:
    # - CRM schema variations
    # - external enrichment systems
    # ------------------------------------------------------
    "address.city":
        ("quality", 0.60),

    "address.state":
        ("quality", 0.60),

    "address.country":
        ("quality", 0.60),
}
```
