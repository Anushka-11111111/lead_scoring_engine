class FieldExtractor:
    """
    Utility class responsible for flattening deeply nested CRM lead data.

    Example:
    Input:
    {
        "company": {
            "name": "OpenAI",
            "employees": 1000
        }
    }

    Output:
    {
        "company.name": "OpenAI",
        "company.employees": 1000
    }

    This makes downstream rule engines, ML pipelines,
    and signal processors easier to work with because
    all fields become accessible through flat keys.
    """

    def extract_all_fields(self, lead: dict) -> dict:
        """
        Converts a nested CRM lead dictionary into a flat dictionary.

        Supports:
        - Nested dictionaries
        - Lists / arrays
        - Primitive values (str, int, float, bool, etc.)

        Args:
            lead (dict):
                Raw CRM lead object.

        Returns:
            dict:
                Flattened dictionary with dot-notation keys.
        """

        # Final flattened output
        flattened = {}

        def safe_key(path, value):
            """
            Stores the flattened key-value pair.

            Example:
            path  = "company.name"
            value = "OpenAI"
            """
            flattened[path] = value

        def walk(prefix, obj):
            """
            Recursive function that traverses the entire CRM payload.

            Parameters:
                prefix (str):
                    Current flattened path.

                obj:
                    Current object being processed.
                    Can be dict, list, or primitive value.
            """

            # Ignore null values completely
            if obj is None:
                return

            # -----------------------------
            # Handle dictionaries
            # -----------------------------
            # Example:
            # {
            #   "company": {
            #       "name": "OpenAI"
            #   }
            # }
            #
            # becomes:
            # company.name
            # -----------------------------
            if isinstance(obj, dict):

                for k, v in obj.items():

                    # Build hierarchical field path
                    new_key = f"{prefix}.{k}" if prefix else k

                    # Recursively process child value
                    walk(new_key, v)

            # -----------------------------
            # Handle lists / arrays
            # -----------------------------
            # Example:
            # {
            #   "emails": ["a@test.com", "b@test.com"]
            # }
            #
            # becomes:
            # emails[0]
            # emails[1]
            # -----------------------------
            elif isinstance(obj, list):

                for i, v in enumerate(obj):

                    # Preserve array index in field path
                    new_key = f"{prefix}[{i}]"

                    # Recursively process list item
                    walk(new_key, v)

            # -----------------------------
            # Handle primitive values
            # -----------------------------
            # Examples:
            # str, int, float, bool
            # -----------------------------
            else:
                safe_key(prefix, obj)

        # Start recursive traversal from root
        walk("", lead)

        return flattened