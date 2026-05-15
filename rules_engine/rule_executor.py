from typing import List
from rules_engine.condition_evaluator import ConditionEvaluator
from core_contracts.rule_trigger import RuleTrigger


class RuleExecutor:
    """
    Core execution engine for the rule-based scoring system.

    Responsibilities:
    - Execute scoring rules against semantic signals
    - Evaluate rule conditions
    - Apply AND/OR logic
    - Generate dynamic scores
    - Produce explainable rule triggers

    This is one of the MOST IMPORTANT components
    in the scoring architecture.

    Pipeline Flow:
        Semantic Signals
              ↓
        Rule Evaluation
              ↓
        Condition Matching
              ↓
        Dynamic Score Calculation
              ↓
        RuleTrigger Generation

    Key Features:
    - Dynamic scoring
    - Explainable rule matching
    - Flexible condition logic
    - Debug execution mode
    - Quality-aware scoring
    """

    def __init__(self):
        """
        Initializes rule execution engine.
        """

        # Core condition evaluation engine
        #
        # Responsible for evaluating:
        # - eq / neq
        # - gt / lt
        # - contains
        # - validation checks
        # - date comparisons
        self.evaluator = ConditionEvaluator()

    # =====================================================
    # MAIN RULE EXECUTION ENGINE
    # =====================================================
    def execute(self, signals, rules) -> List[RuleTrigger]:
        """
        Executes rules against semantic signals.

        Args:
            signals:
                List of SemanticSignal objects.

            rules:
                List of scoring rules.

        Returns:
            List[RuleTrigger]:
                Successfully triggered rules.
        """

        # Final triggered rule collection
        triggers = []

        # --------------------------------------------------
        # Iterate through all scoring rules
        # --------------------------------------------------
        for rule in rules:

            # Skip invalid/empty rules
            if not rule.conditions:
                continue

            # Stores True/False results for each condition
            condition_results = []

            # Tracks fields that matched the rule
            matched_fields = []

            # Initial static score from rule definition
            #
            # May later be dynamically adjusted.
            dynamic_score = float(rule.score)

            # ==================================================
            # CONDITION EVALUATION
            # ==================================================
            for cond in rule.conditions:

                # Tracks whether THIS condition matched
                condition_met = False

                # --------------------------------------------------
                # Compare condition against ALL signals
                # --------------------------------------------------
                for signal in signals:

                    # Evaluate signal-condition match
                    result = self.evaluator.evaluate(
                        signal,
                        cond
                    )

                    # --------------------------------------------------
                    # Successful condition match
                    # --------------------------------------------------
                    if result:

                        condition_met = True

                        # Track matched CRM field
                        matched_fields.append(
                            signal.field_path
                        )

                        # ==================================================
                        # 🔥 DYNAMIC SCORING ENGINE
                        # ==================================================
                        #
                        # Instead of static rule scores,
                        # scoring adapts based on:
                        # - signal values
                        # - freshness
                        # - probabilities
                        # - data quality
                        #
                        # Example:
                        # 90% pipeline probability
                        # should score higher than 60%
                        # ==================================================
                        dynamic_score = (
                            self._calculate_dynamic_score(
                                rule,
                                signal,
                                dynamic_score
                            )
                        )

                        # Stop checking additional signals
                        # once condition already matched.
                        break

                # Store condition outcome
                condition_results.append(condition_met)

            # ==================================================
            # APPLY RULE LOGIC
            # ==================================================
            #
            # Supports:
            # - AND logic
            # - OR logic
            # ==================================================
            final = self._apply_logic(
                condition_results,
                rule.logic
            )

            # --------------------------------------------------
            # Rule successfully triggered
            # --------------------------------------------------
            if final:

                triggers.append(

                    RuleTrigger(

                        # Rule identifier
                        rule_id=rule.rule_id,

                        # Human-readable rule name
                        name=rule.name,

                        # Scoring category
                        category=rule.category,

                        # 🔥 Dynamic final score
                        score=round(dynamic_score, 2),

                        # Fields/signals responsible
                        matched_signals=matched_fields,

                        # Human-readable explanation
                        reason=(
                            rule.description
                            or f"{rule.name} triggered"
                        )
                    )
                )

        return triggers

    # =====================================================
    # DEBUG EXECUTION MODE
    # =====================================================
    def debug_execute(self, signals, rules):
        """
        Executes rules with detailed debugging output.

        Purpose:
        Helps developers understand:
        - Which conditions matched
        - Which signals triggered rules
        - How dynamic scores changed
        - Why rules failed

        Extremely useful during:
        - Rule development
        - CRM integration debugging
        - Scoring optimization
        """

        print("\n🔍 ===== DYNAMIC RULE DEBUGGER =====\n")

        triggers = []

        # --------------------------------------------------
        # Evaluate each rule individually
        # --------------------------------------------------
        for rule in rules:

            # print(f"\n🧠 RULE: {rule.name}")
            # print(f"   LOGIC: {rule.logic}")

            condition_results = []
            matched_fields = []

            # Starting score
            dynamic_score = float(rule.score)

            # --------------------------------------------------
            # Evaluate all rule conditions
            # --------------------------------------------------
            for cond in rule.conditions:

                # print(f"\n   🧩 CONDITION:")
                # print(f"      field   : {cond.field}")
                # print(f"      operator: {cond.operator}")
                # print(f"      value   : {cond.value}")

                condition_met = False

                # --------------------------------------------------
                # Compare against all signals
                # --------------------------------------------------
                for signal in signals:

                    result = self.evaluator.evaluate(
                        signal,
                        cond
                    )

                    if result:

                        # print(
                        #     f"      ✅ MATCHED by: "
                        #     f"{signal.field_path}"
                        # )

                        # print(
                        #     f"      📦 VALUE: "
                        #     f"{signal.value}"
                        # )

                        condition_met = True

                        matched_fields.append(
                            signal.field_path
                        )

                        # ==================================================
                        # Dynamic scoring visualization
                        # ==================================================
                        old_score = dynamic_score

                        dynamic_score = (
                            self._calculate_dynamic_score(
                                rule,
                                signal,
                                dynamic_score
                            )
                        )

                        # print(
                        #     f"      ⚡ Dynamic Score: "
                        #     f"{old_score:.2f} "
                        #     f"→ "
                        #     f"{dynamic_score:.2f}"
                        # )

                        break

                # print(
                #     f"      👉 CONDITION RESULT: "
                #     f"{condition_met}"
                # )

                condition_results.append(condition_met)

            # --------------------------------------------------
            # Apply final AND/OR rule logic
            # --------------------------------------------------
            final = self._apply_logic(
                condition_results,
                rule.logic
            )

            print(f"\n   🧠 FINAL RULE MATCH: {final}")

            # --------------------------------------------------
            # Trigger rule if successful
            # --------------------------------------------------
            if final:

                print(f"   ✅ RULE TRIGGERED")

                print(
                    f"   🎯 FINAL SCORE: "
                    f"{dynamic_score:.2f}"
                )

                triggers.append(
                    RuleTrigger(
                        rule_id=rule.rule_id,
                        name=rule.name,
                        category=rule.category,
                        score=round(dynamic_score, 2),
                        matched_signals=matched_fields,
                        reason=(
                            rule.description
                            or f"{rule.name} triggered"
                        )
                    )
                )

            else:
                print(f"   ❌ RULE NOT TRIGGERED")

        print("\n🔍 ===== DEBUG END =====\n")

        return triggers

    # =====================================================
    # 🔥 DYNAMIC SCORING ENGINE
    # =====================================================
    def _calculate_dynamic_score(
        self,
        rule,
        signal,
        base_score
    ):
        """
        Dynamically adjusts rule score based on
        actual signal values.

        Why dynamic scoring matters:
        Static scores are often unrealistic.

        Example:
            90% win probability
            should score MUCH higher than:
            40% win probability

        This engine creates:
        - More realistic ranking
        - Better prioritization
        - Smarter score distribution
        """

        value = signal.value
        rule_name = rule.name

        try:

            # ==================================================
            # HIGH PIPELINE PROBABILITY
            # ==================================================
            if rule_name == "High Pipeline Probability":

                probability = float(value)

                # --------------------------------------------------
                # Continuous scaling formula
                #
                # Example:
                # 50 → 30
                # 80 → 35
                # --------------------------------------------------
                return min(
                    10 + (probability * 0.4),
                    35
                )

            # ==================================================
            # RECENT LEAD SCORING
            # ==================================================
            if rule_name == "Recent Lead":

                from datetime import datetime

                created = datetime.fromisoformat(
                    str(value).replace("Z", "")
                )

                # Lead age in days
                days_old = (
                    datetime.utcnow() - created
                ).days

                # Fresher leads receive higher scores
                freshness = max(0, 10 - days_old)

                return min(
                    10 + freshness,
                    20
                )

            # ==================================================
            # VALID EMAIL BOOST
            # ==================================================
            if rule_name == "Valid Email":

                email = str(value).lower()

                # Free/public email providers
                #
                # Lower business intent
                if any(
                    x in email
                    for x in [
                        "gmail",
                        "yahoo",
                        "hotmail"
                    ]
                ):
                    return 10

                # Business email domains
                return 18

            # ==================================================
            # VALID PHONE BOOST
            # ==================================================
            if rule_name == "Valid Phone":

                phone = str(value)

                # International/business numbers
                if len(phone) >= 12:
                    return 18

                return 12

            # ==================================================
            # HIGH VALUE GEO TARGETING
            # ==================================================
            if rule_name == "High Value Geography":

                country = str(value).lower()

                # Premium markets
                if country in [
                    "usa",
                    "united states"
                ]:
                    return 25

                if country in [
                    "uk",
                    "united kingdom"
                ]:
                    return 22

                if country == "canada":
                    return 20

                return base_score

        # --------------------------------------------------
        # Fail-safe protection
        #
        # Dynamic scoring should NEVER crash
        # the rule engine.
        # --------------------------------------------------
        except Exception:
            return base_score

        # Default unchanged score
        return base_score

    # =====================================================
    # RULE LOGIC HANDLER
    # =====================================================
    def _apply_logic(self, results, logic):
        """
        Applies AND/OR logic to condition results.

        Args:
            results:
                List of boolean condition outcomes.

            logic:
                Rule logic mode:
                - AND
                - OR

        Returns:
            bool:
                Final rule match result.
        """

        # No conditions evaluated
        if not results:
            return False

        # Default logic = OR
        logic = (logic or "OR").upper()

        # --------------------------------------------------
        # AND logic
        #
        # ALL conditions must match
        # --------------------------------------------------
        if logic == "AND":
            return all(results)

        # --------------------------------------------------
        # OR logic
        #
        # ANY condition may match
        # --------------------------------------------------
        return any(results)