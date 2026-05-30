class ScorePusher:
    """
    Responsible for pushing finalized lead scores
    back into the CRM system.

    Purpose:
    - Synchronize scoring results with CRM
    - Store classifications/confidence
    - Send explainability metadata
    - Enable sales visibility inside CRM

    Typical Flow:
    1. Lead scoring engine computes scores
    2. FinalScore/LeadScore object is generated
    3. ScorePusher sends results to CRM API

    Benefits:
    - Centralized score publishing layer
    - Cleaner separation of responsibilities
    - Easier CRM integration maintenance
    """

    def __init__(self, client):
        """
        Initializes score push service.

        Args:
            client:
                CRM API client responsible for
                authenticated HTTP communication.
        """

        # CRM API client
        self.client = client

    def push_score(self, lead_id, score_payload):
        """
        Pushes finalized lead score data into CRM.

        Data sent includes:
        - Final total score
        - Lead classification
        - Confidence score
        - Score breakdown
        - Explainability reasons

        Args:
            lead_id (str):
                CRM lead identifier.

            score_payload:
                Final scoring object
                (LeadScore / FinalScore / dict).

        Returns:
            dict:
                CRM API response.
        """

        # --------------------------------------------------
        # CRM endpoint for score updates (prefixed with /api/v1)
        # --------------------------------------------------
        endpoint = f"/api/v1/leads/{lead_id}/score"

        # --------------------------------------------------
        # Request payload sent to CRM
        # --------------------------------------------------
        if isinstance(score_payload, dict):
            # If the payload is already a dictionary formatted as crm_payload
            body = score_payload
        else:
            # Fallback for LeadScore/FinalScore dataclasses
            body = {
                # Final aggregated lead score
                "score": getattr(score_payload, "total_score", 0),

                # Lead classification
                "classification": getattr(score_payload, "classification", "Cold Lead"),

                # Confidence/reliability score
                "confidence": getattr(score_payload, "confidence", 0),

                # Detailed scoring breakdown
                "breakdown": {
                    "fit": getattr(score_payload, "fit_score", 0),
                    "behavior": getattr(score_payload, "behavior_score", 0),
                    "quality": getattr(score_payload, "quality_score", 0),
                    "penalty": getattr(score_payload, "penalty_score", 0)
                },

                # Human-readable scoring explanations
                "reasons": getattr(score_payload, "reasons", []) or getattr(score_payload, "explanations", [])
            }

        # --------------------------------------------------
        # Send POST request to CRM
        # --------------------------------------------------
        return self.client.post(endpoint, body)