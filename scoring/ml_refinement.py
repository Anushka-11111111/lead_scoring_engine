import joblib
import os
import logging
import numpy as np
import pandas as pd

from typing import Dict, Any

# ----------------------------------------------------------
# Central logger
# ----------------------------------------------------------
logger = logging.getLogger(__name__)


class MLRefinementLayer:
    """
    Hybrid ML refinement engine.

    Combines:
    - Rule-based scoring
    - ML probability estimation
    """

    def __init__(self, model_dir: str = "models"):

        self.model_dir = model_dir

        self._model = None
        self._scaler = None
        self._config = None

        self._load_artifacts()

    # ======================================================
    # MODEL ARTIFACT LOADING
    # ======================================================
    def _load_artifacts(self):
        """
        Loads ML artifacts.

        Required files:
        - hybrid_model_v2_0.joblib
        - scaler_v2_0.joblib
        - hybrid_config_v2_0.pkl
        """

        try:

            # --------------------------------------------------
            # Trained ML model
            # --------------------------------------------------
            self._model = joblib.load(

                os.path.join(
                    self.model_dir,
                    "hybrid_model_v2_0.joblib"
                )
            )

            # --------------------------------------------------
            # Feature scaler
            # --------------------------------------------------
            self._scaler = joblib.load(

                os.path.join(
                    self.model_dir,
                    "scaler_v2_0.joblib"
                )
            )

            # --------------------------------------------------
            # Config / metadata
            # --------------------------------------------------
            self._config = joblib.load(

                os.path.join(
                    self.model_dir,
                    "hybrid_config_v2_0.pkl"
                )
            )

            logger.info(
                "✅ ML Refinement Layer loaded"
            )

        except Exception as e:

            logger.warning(
                f"⚠️ ML artifacts failed: {e}"
            )

    # ======================================================
    # FEATURE MAPPING ENGINE
    # ======================================================
    def _map_features(
        self,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        mapped = {}

        ignore_keys = {

            "id",
            "_id",
            "sf_id",
            "contact_id",
            "lead_id",
            "ct_id"
        }

        for k, v in lead_data.items():

            if k.lower() in ignore_keys:
                continue

            key = k.lower().strip()

            # Lead age
            if any(
                x in key
                for x in ["age", "days_old"]
            ):

                mapped["Lead Age (Days)"] = v

            # Revenue
            elif any(
                x in key
                for x in ["revenue", "annual"]
            ):

                mapped["Annual Revenue (INR)"] = v

            # Employees
            elif any(
                x in key
                for x in [
                    "employee",
                    "headcount",
                    "size"
                ]
            ):

                mapped["Employee Count"] = v

            # Industry
            elif any(
                x in key
                for x in [
                    "industry",
                    "vertical"
                ]
            ):

                mapped["Industry"] = v

            # Source
            elif any(
                x in key
                for x in [
                    "source",
                    "channel"
                ]
            ):

                mapped["Source"] = v

            # Stage
            elif any(
                x in key
                for x in [
                    "stage",
                    "pipeline"
                ]
            ):

                mapped["Lead Stage"] = v

            # Segment
            elif any(
                x in key
                for x in [
                    "segment",
                    "tier"
                ]
            ):

                mapped["Lead Segment"] = v

            # Geography
            elif any(
                x in key
                for x in [
                    "country",
                    "region"
                ]
            ):

                mapped["Country"] = v

            # Email
            elif "email" in key:

                mapped["Email"] = v

            # Phone
            elif "phone" in key:

                mapped["Phone"] = v

        return mapped

    # ======================================================
    # MAIN ML REFINEMENT ENGINE
    # ======================================================
    def refine(
        self,
        lead_data: Dict[str, Any],
        rule_score: float,
        debug: bool = False
    ) -> Dict[str, Any]:

        # --------------------------------------------------
        # ML unavailable fallback
        # --------------------------------------------------
        if self._model is None:

            return {

                "ml_score": rule_score,

                "ml_prediction":
                    int(rule_score >= 50),

                "ml_probability":
                    rule_score / 100.0,

                "confidence": 0.5,

                "warning":
                    "ML not loaded"
            }

        try:

            # ==================================================
            # FEATURE MAPPING
            # ==================================================
            mapped = self._map_features(
                lead_data
            )

            feats = []

            matched = 0

            # ==================================================
            # FEATURE VECTOR CONSTRUCTION
            # ==================================================
            for fname in self._config["feature_names"]:

                # Rule score injection
                if fname == "rule_score_norm":

                    feats.append(
                        rule_score / 100.0
                    )

                # Direct mapped features
                elif fname in mapped:

                    val = mapped[fname]

                    try:

                        feats.append(

                            float(val)

                            if pd.notna(val)

                            else 0.0
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        feats.append(0.0)

                    matched += 1

                # Presence features
                elif fname.startswith("has_"):

                    base = fname.replace(
                        "has_",
                        ""
                    )

                    feats.append(

                        1.0

                        if mapped.get(base)

                        else 0.0
                    )

                # Missing feature fallback
                else:

                    feats.append(0.0)

            # ==================================================
            # DEBUG LOGGING
            # ==================================================
            if debug:

                logger.info(

                    f"🔍 ML matched: "

                    f"{matched}/"

                    f"{len(self._config['feature_names'])} "

                    f"features"
                )

            # ==================================================
            # FEATURE MATRIX
            # ==================================================
            X = np.array(feats).reshape(1, -1)

            # Scale features
            X_scaled = self._scaler.transform(X)

            # ==================================================
            # PREDICTION
            # ==================================================
            prob = float(

                self._model
                .predict_proba(X_scaled)[0][1]
            )

            # ==================================================
            # DEBUG PROBABILITY
            # ==================================================
            if debug:

                logger.info(

                    f"📊 Raw Prob: {prob:.4f} "

                    f"| Rule: {rule_score:.2f}"
                )

            # ==================================================
            # FINAL OUTPUT
            # ==================================================
            return {

                "ml_score":
                    round(prob * 100, 2),

                "ml_prediction":

                    int(
                        prob >= self._config.get(
                            "threshold",
                            0.3
                        )
                    ),

                "ml_probability":
                    round(prob, 4),

                "confidence":

                    round(
                        1 - abs(0.5 - prob),
                        4
                    )
            }

        # --------------------------------------------------
        # SAFE FALLBACK
        # --------------------------------------------------
        except Exception as e:

            logger.warning(
                f"⚠️ ML failed: {e}"
            )

            return {

                "ml_score": rule_score,

                "ml_prediction":
                    int(rule_score >= 50),

                "ml_probability":
                    rule_score / 100.0,

                "confidence": 0.5,

                "warning": str(e)
            }