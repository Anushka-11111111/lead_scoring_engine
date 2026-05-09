class CRMAuth:
    """
    Handles CRM authentication/session management
    using browser cookies.

    Purpose:
    - Converts raw browser cookie strings into
      request-compatible cookie dictionaries
    - Generates standard HTTP headers
    - Supports authenticated CRM API requests

    Typical Usage:
    auth = CRMAuth(cookie_string)

    requests.get(
        url,
        headers=auth.get_headers(),
        cookies=auth.get_cookies()
    )

    Why both headers + cookies?
    Some CRM/backend systems:
    - Validate the raw "Cookie" header directly
    - Require a proper cookie jar simultaneously

    This class supports both approaches for maximum compatibility.
    """

    def __init__(self, cookie_string=None):
        """
        Initializes authentication manager.

        Args:
            cookie_string (str):
                Raw browser cookie string copied
                from browser dev tools/network tab.

        Example:
            "sessionid=abc123; csrftoken=xyz456"
        """

        # Raw browser cookie string
        self.cookie_string = cookie_string

    def _parse_cookie_string(self):
        """
        Converts raw cookie string into
        a Python dictionary.

        Example:
            Input:
                "a=1; b=2"

            Output:
                {
                    "a": "1",
                    "b": "2"
                }

        This format is required by:
            requests(..., cookies={...})

        Returns:
            dict:
                Parsed cookie key-value pairs.
        """

        # Final parsed cookie dictionary
        cookies = {}

        # No cookies provided
        if not self.cookie_string:
            return cookies

        # Split cookies by semicolon
        # Example:
        # "a=1; b=2" → ["a=1", " b=2"]
        parts = self.cookie_string.split(";")

        for part in parts:

            # Ensure valid key=value structure
            if "=" in part:

                # Split only on first "="
                # Prevents issues if values contain "="
                key, value = part.strip().split("=", 1)

                cookies[key] = value

        return cookies

    def get_headers(self):
        """
        Generates HTTP headers for CRM API requests.

        Includes:
        - Standard browser-like headers
        - Content negotiation headers
        - Raw cookie header

        Browser-like headers help:
        - Prevent bot blocking
        - Improve compatibility
        - Mimic real browser sessions

        Returns:
            dict:
                HTTP request headers.
        """

        return {

            # Accept any response type
            "Accept": "*/*",

            # JSON request payloads
            "Content-Type": "application/json",

            # Browser user agent
            # Helps mimic real browser traffic
            "User-Agent": "Mozilla/5.0",

            # Request origin
            "Origin": "https://app.togile.com",

            # Referring page
            "Referer": "https://app.togile.com/",

            # --------------------------------------------------
            # Raw cookie header
            #
            # IMPORTANT:
            # Some servers validate cookies directly
            # from headers instead of cookie jars.
            #
            # Keeping this improves compatibility.
            # --------------------------------------------------
            "Cookie": self.cookie_string
        }

    def get_cookies(self):
        """
        Returns cookies in requests-compatible format.

        IMPORTANT:
        The Python requests library internally manages
        cookies better when provided as a dictionary.

        Example:
            requests.get(
                url,
                cookies={"sessionid": "abc"}
            )

        Returns:
            dict:
                Parsed cookie dictionary.
        """

        # 🔥 CRITICAL:
        # requests will automatically construct
        # a proper cookie jar from this dictionary.
        return self._parse_cookie_string()