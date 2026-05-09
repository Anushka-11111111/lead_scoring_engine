from typing import Any, Dict, List, Tuple


class CRMFlattener:
    """
    Universal CRM JSON flattening engine.

    Purpose:
    Converts deeply nested CRM payloads into
    flat path-based structures.

    Why flattening is important:
    CRM systems usually return highly nested JSON.

    Example:
    {
        "contact": {
            "email": "test@gmail.com"
        }
    }

    becomes:

    contact.email → test@gmail.com

    Flattening enables:
    - easier rule matching
    - signal extraction
    - feature engineering
    - ML processing
    - indexing/searching
    - analytics pipelines

    Output Structure:
        (path, value, depth)

    Example:
        ("contact.email", "abc@gmail.com", 2)
    """

    def __init__(self, separator: str = "."):
        """
        Initializes flattening engine.

        Args:
            separator:
                Character used to join nested keys.

                Example:
                    contact.email

                Default:
                    "."
        """

        # Separator used in flattened paths
        self.separator = separator

    # ==================================================
    # MAIN FLATTEN FUNCTION
    # ==================================================
    def flatten(
        self,
        data: Any
    ) -> List[Tuple[str, Any, int]]:
        """
        Public flattening entry point.

        Args:
            data:
                Any nested CRM payload
                (dict/list/primitives)

        Returns:
            List of tuples:
                (
                    flattened_path,
                    value,
                    depth
                )

        Example Output:
            [
                ("contact.email", "a@gmail.com", 2),
                ("company.name", "Acme", 2)
            ]
        """

        # Final flattened storage
        results = []

        # Begin recursive traversal
        self._flatten_recursive(

            data,

            "",

            0,

            results
        )

        return results

    # ==================================================
    # RECURSIVE FLATTENING ENGINE
    # ==================================================
    def _flatten_recursive(
        self,
        current: Any,
        path: str,
        depth: int,
        results: List[Tuple[str, Any, int]],
    ):
        """
        Recursive traversal engine.

        Traverses:
        - dictionaries
        - lists
        - primitive values

        and converts them into flat records.

        Args:
            current:
                Current object being traversed

            path:
                Current flattened path

            depth:
                Current nesting depth

            results:
                Shared mutable output list
        """

        # ==================================================
        # CASE 1: DICTIONARY OBJECT
        # ==================================================
        if isinstance(current, dict):

            # --------------------------------------------------
            # Empty dictionary handling
            #
            # Important because:
            # empty dicts still represent
            # meaningful CRM state.
            # --------------------------------------------------
            if not current:

                results.append(

                    (
                        path,
                        current,
                        depth
                    )
                )

                return

            # --------------------------------------------------
            # Traverse all dictionary keys
            # --------------------------------------------------
            for key, value in current.items():

                # Build flattened path
                #
                # Example:
                # contact.email
                # company.name
                # --------------------------------------------------
                new_path = (

                    f"{path}{self.separator}{key}"

                    if path

                    else key
                )

                # Recursive descent
                self._flatten_recursive(

                    value,

                    new_path,

                    depth + 1,

                    results
                )

        # ==================================================
        # CASE 2: LIST / ARRAY
        # ==================================================
        elif isinstance(current, list):

            # --------------------------------------------------
            # Empty list handling
            # --------------------------------------------------
            if not current:

                results.append(

                    (
                        path,
                        current,
                        depth
                    )
                )

                return

            # --------------------------------------------------
            # Traverse array items
            # --------------------------------------------------
            for index, item in enumerate(current):

                # Preserve array indexing
                #
                # Example:
                # phones[0]
                # phones[1]
                # --------------------------------------------------
                new_path = f"{path}[{index}]"

                # Recursive descent
                self._flatten_recursive(

                    item,

                    new_path,

                    depth + 1,

                    results
                )

        # ==================================================
        # CASE 3: PRIMITIVE VALUE
        # ==================================================
        #
        # Primitive examples:
        # - string
        # - int
        # - float
        # - bool
        # - None
        #
        # Final leaf node reached.
        # ==================================================
        else:

            results.append(

                (
                    path,
                    current,
                    depth
                )
            )