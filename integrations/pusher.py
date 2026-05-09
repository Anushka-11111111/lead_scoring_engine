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
                (LeadScore / FinalScore).

        Returns:
            dict:
                CRM API response.
        """

        # --------------------------------------------------
        # CRM endpoint for score updates
        #
        # Example:
        # /leads/123/score
        # --------------------------------------------------
        endpoint = f"/leads/{lead_id}/score"

        # --------------------------------------------------
        # Request payload sent to CRM
        # --------------------------------------------------
        body = {

            # Final aggregated lead score
            "score": score_payload.total_score,

            # Lead classification
            # Example:
            # hot / warm / cold
            "classification": score_payload.classification,

            # Confidence/reliability score
            "confidence": score_payload.confidence,

            # ----------------------------------------------
            # Detailed scoring breakdown
            #
            # Useful for:
            # - CRM dashboards
            # - Explainability
            # - Sales visibility
            # ----------------------------------------------
            "breakdown": {

                # ICP / fit scoring
                "fit": score_payload.fit_score,

                # Engagement/intent scoring
                "behavior": score_payload.behavior_score,

                # Data quality scoring
                "quality": score_payload.quality_score,

                # Risk/penalty deductions
                "penalty": score_payload.penalty_score
            },

            # --------------------------------------------------
            # Human-readable scoring explanations
            #
            # Example:
            # [
            #   "Business email detected",
            #   "Recent CRM activity found"
            # ]
            # --------------------------------------------------
            "reasons": score_payload.reasons
        }

        # --------------------------------------------------
        # Send POST request to CRM
        # --------------------------------------------------
        return self.client.post(endpoint, body)