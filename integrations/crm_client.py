import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


class CRMClient:
    """
    Generic CRM API client used for communicating
    with external CRM systems.
    """

    def __init__(self, base_url, auth):

        # Remove trailing slash
        self.base_url = base_url.rstrip("/")

        # Authentication handler
        self.auth = auth

    # =========================================
    # HEADERS
    # =========================================

    def _get_headers(self):

        return {

            "Accept": "*/*",

            "Content-Type": "application/json",

            "Origin": "https://app.togile.com",

            "Referer": "https://app.togile.com/",

            "User-Agent": "Mozilla/5.0",

            # Auth headers
            **self.auth.get_headers()
        }

    # =========================================
    # COOKIES
    # =========================================

    def _get_cookies(self):

        return self.auth.get_cookies()

    # =========================================
    # GENERIC PUT
    # =========================================

    def put(self, endpoint, payload=None):

        # Build full URL
        url = f"{self.base_url}{endpoint}"

        try:

            # =========================================
            # REQUEST
            # =========================================

            response = requests.put(

                url,

                json=payload,

                headers=self._get_headers(),

                cookies=self._get_cookies(),

                # ✅ SSL FIX
                verify=False,

                timeout=60
            )

            # =========================================
            # DEBUG LOGGING
            # =========================================

            print(f"\n🌐 PUT: {url}")

            print("📤 PAYLOAD:", payload)

            print(f"🔁 STATUS: {response.status_code}")

            print("📦 RAW RESPONSE:")

            print(response.text[:1000])

            # =========================================
            # JSON PARSE
            # =========================================

            try:

                return response.json()

            except Exception:

                raise Exception(
                    f"\n❌ NOT JSON RESPONSE\n"
                    f"Status: {response.status_code}\n"
                    f"Body: {response.text[:300]}"
                )

        except Exception as e:

            print(f"\n❌ CRM REQUEST FAILED: {e}")

            return {
                "success": False,
                "error": str(e)
            }

    # =========================================
    # UPDATE LEAD
    # =========================================

    def update_lead(self, lead_id, payload):

        endpoint = f"/lead/{lead_id}"

        return self.put(endpoint, payload)