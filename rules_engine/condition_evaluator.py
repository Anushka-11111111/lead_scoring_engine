import re
from datetime import datetime


def normalize(text):
    """
    Normalizes text values for safer comparisons.

    Purpose:
    CRM data is often inconsistent:
    - Different casing
    - Extra spaces
    - Mixed formats

    This helper standardizes values before evaluation.

    Example:
        "  USA "
        → "usa"

    Used heavily in:
    - Rule comparisons
    - String matching
    - Equality checks
    """

    return str(text).strip().lower()


def normalize_path(path: str) -> str:
    """
    Normalizes CRM field paths.

    Specifically removes array indexes from paths.

    Example:
        sf_phone_number[0].value
        → sf_phone_number.value

    Why this matters:
    CRM APIs frequently return array-based structures,
    but business rules should not depend on index positions.

    Without normalization:
        sf_phone_number[0].value
        !=
        sf_phone_number.value

    With normalization:
        Both become identical.

    Args:
        path (str):
            Original CRM field path.

    Returns:
        str:
            Normalized field path.
    """

    # Safety fallback
    if not path:
        return ""

    # Normalize casing
    path = str(path).lower()

    # Remove array indexes:
    # [0], [1], [25], etc.
    return re.sub(r"\[\d+\]", "", path)


class ConditionEvaluator:
    """
    Core rule-engine condition evaluator.

    Purpose:
    Evaluates whether a SemanticSignal satisfies
    a specific rule condition.

    This is one of the MOST IMPORTANT components
    of the rule engine.

    Responsibilities:
    - Field matching
    - Operator evaluation
    - Type-safe comparisons
    - Validation checks
    - Date calculations
    - Signal intelligence evaluation

    Example:
        Rule:
            sf_country == "usa"

        Signal:
            sf_country = "USA"

        Result:
            True

    Supported Operator Categories:
    - Equality
    - Numeric comparison
    - String matching
    - Membership checks
    - Regex matching
    - Email validation
    - Phone validation
    - Existence checks
    - Date recency logic
    """

    def evaluate(self, signal, condition) -> bool:
        """
        Evaluates whether a signal matches
        a rule condition.

        Args:
            signal:
                SemanticSignal object.

            condition:
                Rule condition object containing:
                - field
                - operator
                - value

        Returns:
            bool:
                True if condition matches,
                otherwise False.
        """

        # --------------------------------------------------
        # Normalize condition field path
        # --------------------------------------------------
        field = normalize_path(condition.field)

        # Rule operator
        operator = condition.operator

        # Target comparison value
        target = condition.value

        # --------------------------------------------------
        # Normalize signal field path
        # --------------------------------------------------
        signal_field = normalize_path(signal.field_path)

        # Actual CRM value
        signal_value = signal.value

        # ==================================================
        # ✅ SMART FIELD MATCHING
        # ==================================================
        #
        # Handles nested/array CRM inconsistencies.
        #
        # Examples:
        #
        # sf_phone_number.value
        # ==
        # sf_phone_number[0].value
        #
        # sf_email
        # ==
        # sf_email[0]
        #
        # Supports:
        # - exact match
        # - nested field match
        # - parent-child path relationships
        # ==================================================
        if not (
            signal_field == field
            or signal_field.startswith(field + ".")
            or field.startswith(signal_field + ".")
        ):
            return False

        try:

            # ==================================================
            # BASIC COMPARISON OPERATORS
            # ==================================================

            # --------------------------------------------------
            # Equality
            # --------------------------------------------------
            if operator == "eq":
                return normalize(signal_value) == normalize(target)

            # --------------------------------------------------
            # Not equal
            # --------------------------------------------------
            if operator == "neq":
                return normalize(signal_value) != normalize(target)

            # --------------------------------------------------
            # Greater than
            # --------------------------------------------------
            if operator == "gt":
                return float(signal_value) > float(target)

            # --------------------------------------------------
            # Less than
            # --------------------------------------------------
            if operator == "lt":
                return float(signal_value) < float(target)

            # --------------------------------------------------
            # Greater than or equal
            # --------------------------------------------------
            if operator == "gte":
                return float(signal_value) >= float(target)

            # --------------------------------------------------
            # Less than or equal
            # --------------------------------------------------
            if operator == "lte":
                return float(signal_value) <= float(target)

            # ==================================================
            # STRING OPERATORS
            # ==================================================

            # --------------------------------------------------
            # Contains substring
            # --------------------------------------------------
            if operator == "contains":
                return normalize(target) in normalize(signal_value)

            # --------------------------------------------------
            # Membership check
            #
            # Example:
            # signal_value in ["usa", "uk", "canada"]
            # --------------------------------------------------
            if operator == "in":
                return normalize(signal_value) in [
                    normalize(v) for v in target
                ]

            # --------------------------------------------------
            # Regex pattern match
            # --------------------------------------------------
            if operator == "regex":
                return re.search(
                    str(target),
                    str(signal_value)
                ) is not None

            # ==================================================
            # EMAIL VALIDATION
            # ==================================================
            if operator == "valid_email":

                # Empty email
                if not signal_value:
                    return False

                email = str(signal_value).strip().lower()

                # --------------------------------------------------
                # Email format validation
                # --------------------------------------------------
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    return False

                # --------------------------------------------------
                # Fake/test/spam email detection
                # --------------------------------------------------
                blocked = [
                    "test",
                    "fake",
                    "demo",
                    "temp",
                    "dummy"
                ]

                # Reject suspicious emails
                if any(word in email for word in blocked):
                    return False

                return True

            # ==================================================
            # PHONE VALIDATION
            # ==================================================
            if operator == "valid_phone":

                # Missing phone
                if not signal_value:
                    return False

                # Keep only digits
                phone = re.sub(r"\D", "", str(signal_value))

                # --------------------------------------------------
                # Too short → invalid
                # --------------------------------------------------
                if len(phone) < 10:
                    return False

                # --------------------------------------------------
                # Detect spam/fake repeated digits
                #
                # Example:
                # 1111111111
                # 9999999999
                # --------------------------------------------------
                if len(set(phone)) < 3:
                    return False

                return True

            # ==================================================
            # EXISTS / MISSING CHECKS
            # ==================================================

            # --------------------------------------------------
            # Field exists
            # --------------------------------------------------
            if operator == "exists":
                return signal_value not in [
                    None,
                    "",
                    [],
                    {},
                    "null"
                ]

            # --------------------------------------------------
            # Field missing
            # --------------------------------------------------
            if operator == "missing":
                return signal_value in [
                    None,
                    "",
                    [],
                    {},
                    "null"
                ]

            # ==================================================
            # DATE / RECENCY OPERATORS
            # ==================================================

            # --------------------------------------------------
            # Check if date is within X days
            #
            # Example:
            # created_at < 7 days old
            # --------------------------------------------------
            if operator == "less_than_days":

                if not signal_value:
                    return False

                # Parse ISO datetime
                created = datetime.fromisoformat(
                    str(signal_value).replace("Z", "")
                )

                # Compute age in days
                delta = (
                    datetime.utcnow() - created
                ).days

                return delta < int(target)

        # --------------------------------------------------
        # Fail-safe protection
        #
        # Rule evaluation should NEVER crash
        # the entire scoring pipeline.
        # --------------------------------------------------
        except Exception:
            return False

        # Unsupported operator fallback
        return False