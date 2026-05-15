class CRMAuth:

    def __init__(self, cookies):

        # Raw Playwright cookies
        self.cookies = cookies

    def get_cookies(self):

        """
        Convert Playwright cookie list
        into requests-compatible cookie dict.
        """

        cookie_dict = {}

        for cookie in self.cookies:

            cookie_dict[cookie["name"]] = cookie["value"]

        return cookie_dict

    def get_headers(self):

        """
        Optional additional headers.
        Most auth is handled through cookies.
        """

        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": "https://app.togile.com",
            "Referer": "https://app.togile.com/",
            "User-Agent": "Mozilla/5.0"
        }