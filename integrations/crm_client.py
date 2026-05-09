import requests


class CRMClient:
    """
    Generic CRM API client used for communicating
    with external CRM systems.

    Responsibilities:
    - Build authenticated HTTP requests
    - Manage headers/cookies
    - Handle API responses
    - Provide reusable request wrappers
    - Centralize CRM update operations

    Design Goal:
    Keep all CRM communication logic isolated
    inside a single reusable client layer.

    Benefits:
    - Easier debugging
    - Easier CRM migration
    - Cleaner business logic
    - Centralized authentication handling
    """

    def __init__(self, base_url, auth):
        """
        Initializes CRM client.

        Args:
            base_url (str):
                Base CRM API URL.

            auth (CRMAuth):
                Authentication/session manager.
        """

        # Remove trailing slash to avoid:
        # https://api.com//endpoint
        self.base_url = base_url.rstrip("/")

        # Authentication handler
        self.auth = auth

    def _get_headers(self):
        """
        Builds request headers for CRM API calls.

        Combines:
        - Standard browser-like headers
        - Authentication headers

        Browser-like headers help:
        - Prevent bot detection
        - Improve compatibility
        - Mimic real frontend traffic

        Returns:
            dict:
                Final request headers.
        """

        return {

            # Accept all response formats
            "Accept": "*/*",

            # JSON payload format
            "Content-Type": "application/json",

            # Frontend origin simulation
            "Origin": "https://app.togile.com",

            # Referrer page
            "Referer": "https://app.togile.com/",

            # Browser-like user agent
            "User-Agent": "Mozilla/5.0",

            # Merge authentication headers
            **self.auth.get_headers()
        }

    def _get_cookies(self):
        """
        Retrieves authenticated cookie jar
        from authentication manager.

        Returns:
            dict:
                Parsed request cookies.
        """

        return self.auth.get_cookies()

    # --------------------------------------------------
    # 🔁 GENERIC PUT REQUEST
    # --------------------------------------------------
    def put(self, endpoint, payload=None):
        """
        Executes a generic authenticated HTTP PUT request.

        Used for:
        - Updating CRM records
        - Modifying lead fields
        - Sending scoring results back to CRM

        Args:
            endpoint (str):
                API endpoint path.

            payload (dict):
                JSON request body.

        Returns:
            dict:
                Parsed JSON response.

        Raises:
            Exception:
                If API response is not valid JSON.
        """

        # Build full endpoint URL
        url = f"{self.base_url}{endpoint}"

        # --------------------------------------------------
        # Execute HTTP PUT request
        # --------------------------------------------------
        response = requests.put(
            url,

            # Automatically serialized JSON payload
            json=payload,

            # Authenticated request headers
            headers=self._get_headers(),

            # Session cookies
            cookies=self._get_cookies()
        )

        # --------------------------------------------------
        # Debug Logging
        # Extremely useful during CRM integrations
        # --------------------------------------------------

        print(f"\n🌐 PUT: {url}")

        print("📤 PAYLOAD:", payload)

        print(f"🔁 STATUS: {response.status_code}")

        # Limit response preview size
        print("📦 RAW RESPONSE:", response.text[:500])

        # --------------------------------------------------
        # Attempt JSON parsing
        # --------------------------------------------------
        try:
            return response.json()

        # Non-JSON response handling
        except Exception:

            # Some CRMs return:
            # - HTML error pages
            # - Empty responses
            # - Invalid JSON
            raise Exception(
                f"\n❌ NOT JSON RESPONSE\n"
                f"Status: {response.status_code}\n"
                f"Body: {response.text[:300]}"
            )

    # --------------------------------------------------
    # ✅ UPDATE LEAD WRAPPER
    # --------------------------------------------------
    def update_lead(self, lead_id, payload):
        """
        Centralized helper method for updating
        a CRM lead record.

        Why this wrapper exists:
        Instead of scattering endpoint paths
        across the codebase, all lead update logic
        stays centralized here.

        If CRM endpoints change later,
        only THIS method needs modification.

        Args:
            lead_id (str):
                CRM lead identifier.

            payload (dict):
                Fields/data to update.

        Returns:
            dict:
                CRM API response.
        """

        # --------------------------------------------------
        # CRM lead update endpoint
        #
        # IMPORTANT:
        # Modify ONLY this path if CRM API changes.
        # --------------------------------------------------
        endpoint = f"/lead/{lead_id}"

        # Reuse generic PUT handler
        return self.put(endpoint, payload)