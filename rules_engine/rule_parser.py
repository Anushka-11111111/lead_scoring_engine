import json
from typing import List
from rules_engine.rule_model import Rule, Condition


class RuleParser:
    """
    Responsible for loading and parsing rule definitions
    from external JSON configuration files.

    Purpose:
    Converts raw JSON rule definitions into strongly-typed
    Rule and Condition objects used by the rule engine.

    Why this layer matters:
    - Keeps business logic configurable
    - Allows non-code rule updates
    - Enables scalable rule management
    - Separates logic from implementation

    Example Flow:
        rules.json
            ↓
        RuleParser
            ↓
        Rule objects
            ↓
        RuleExecutor

    Benefits:
    - Dynamic rule updates
    - Cleaner architecture
    - Easier testing/debugging
    - Business-friendly configuration
    """

    def load_rules(self, path: str) -> List[Rule]:
        """
        Loads and parses rules from a JSON file.

        Args:
            path (str):
                Path to rules.json file.

        Returns:
            List[Rule]:
                Parsed rule objects ready
                for execution.

        Raises:
            ValueError:
                If JSON structure is invalid.
        """

        # --------------------------------------------------
        # Load raw JSON file
        # --------------------------------------------------
        with open(path, "r") as f:
            raw_rules = json.load(f)

        # --------------------------------------------------
        # Validate root structure
        #
        # Expected:
        # [
        #   {...rule1...},
        #   {...rule2...}
        # ]
        # --------------------------------------------------
        if not isinstance(raw_rules, list):
            raise ValueError(
                "rules.json must be a list"
            )

        # Final parsed rule collection
        rules = []

        # --------------------------------------------------
        # Parse each raw rule
        # --------------------------------------------------
        for r in raw_rules:

            # Safety validation
            if not isinstance(r, dict):
                raise ValueError(
                    f"Invalid rule format: {r}"
                )

            # ==================================================
            # ✅ SAFE CONDITION PARSING
            # ==================================================
            #
            # Converts raw JSON conditions into
            # strongly-typed Condition objects.
            #
            # Example JSON:
            # {
            #   "field": "sf_country",
            #   "operator": "eq",
            #   "value": "usa"
            # }
            # ==================================================
            conditions = []

            for c in r.get("conditions", []):

                # Validate condition structure
                if not isinstance(c, dict):
                    raise ValueError(
                        f"Invalid condition: {c}"
                    )

                # --------------------------------------------------
                # Build Condition object
                # --------------------------------------------------
                condition = Condition(

                    # CRM/signal field
                    field=c.get("field"),

                    # Comparison operator
                    operator=c.get("operator"),

                    # Target comparison value
                    #
                    # 🔥 Important Fix:
                    # Default to None if missing
                    # instead of crashing.
                    value=c.get("value", None)
                )

                conditions.append(condition)

            # ==================================================
            # Build Rule object
            # ==================================================
            rule = Rule(

                # Unique rule identifier
                rule_id=r.get("rule_id"),

                # Human-readable rule name
                name=r.get(
                    "name",
                    "Unnamed Rule"
                ),

                # Rule scoring category
                #
                # Examples:
                # - fit
                # - behavior
                # - quality
                # - penalty
                category=r.get(
                    "category",
                    "general"
                ),

                # Base rule score
                score=r.get("score", 0),

                # Parsed conditions
                conditions=conditions,

                # Logical evaluation mode
                #
                # Supported:
                # - AND
                # - OR
                logic=r.get("logic", "AND"),

                # Optional explanation
                description=r.get(
                    "description",
                    ""
                )
            )

            # Store parsed rule
            rules.append(rule)

        # --------------------------------------------------
        # Final validated rule set
        # --------------------------------------------------
        return rules