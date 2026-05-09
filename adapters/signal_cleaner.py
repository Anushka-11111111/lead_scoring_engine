class SignalCleaner:
    """
    Cleans extracted CRM observations before they are sent
    into the scoring engine or ML pipeline.

    Purpose:
    - Removes unusable values
    - Prevents noisy CRM data from affecting scoring
    - Standardizes input quality for downstream systems

    Example:
    Input:
    {
        "company.name": "OpenAI",
        "phone": "",
        "industry": "unknown"
    }

    Output:
    {
        "company.name": "OpenAI"
    }
    """

    def clean(self, observations):
        """
        Removes invalid or junk values from observation data.

        Args:
            observations (dict):
                Flattened CRM lead signals/fields.

        Returns:
            dict:
                Cleaned dictionary containing only valid values.
        """

        # Stores cleaned output
        cleaned = {}

        # Iterate through all extracted observations
        for k, v in observations.items():

            # -----------------------------------
            # Remove junk / unusable values
            # -----------------------------------
            # These values commonly appear in CRMs
            # when fields are missing or improperly filled.
            # -----------------------------------
            if v in [None, "", "unknown", "null"]:
                continue

            # Keep valid signal
            cleaned[k] = v

        return cleaned
