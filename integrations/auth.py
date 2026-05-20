import os
from dotenv import load_dotenv

load_dotenv()


class CRMAuth:

    def __init__(self):

        # =========================================
        # JWT TOKEN FROM .env
        # =========================================

        self.token = os.getenv("TOGILE_TOKEN")

        if not self.token:

            raise Exception(
                "❌ TOGILE_TOKEN missing in .env"
            )

    # =========================================
    # HEADERS
    # =========================================

    def get_headers(self):

        return {

            "Authorization": (
                f"Bearer {self.token}"
            ),

            "Accept": "*/*",

            "Content-Type": "application/json",

            "Origin": "https://app.togile.com",

            "Referer": "https://app.togile.com/",

            "User-Agent": "Mozilla/5.0"
        }

    # =========================================
    # COOKIES
    # =========================================

    def get_cookies(self):

        return {

            "token": self.token
        }