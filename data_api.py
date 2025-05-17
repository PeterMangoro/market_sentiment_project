import requests
from api_keys import TWITTER_API_KEY

class ApiClient:
    def __init__(self, api_key=None):
        self.base_url = "https://api.twitter.com/2"  # Replace with actual base URL
        self.api_key = api_key or TWITTER_API_KEY  # Or load from environment

    def call_api(self, endpoint, query=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        try:
            response = requests.get(url, headers=headers, params=query)
            response.raise_for_status()
            return response.json()  # or response.text if not JSON
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {e}")
            return None
