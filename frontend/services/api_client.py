from typing import Any, Dict, List, Tuple

import requests

from config import BACKEND_URL
from models.place import Place


class ApiClient:
    def __init__(self, base_url: str = BACKEND_URL, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=3)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {"backend": "offline", "llm_enabled": False, "places_enabled": False}

    def get_recommendations(
        self,
        ui_prefs: Dict[str, Any],
        user_query: str,
        location: Dict[str, Any],
        location_name: str,
        taste_profile: Dict[str, Any],
    ) -> Tuple[List[Place], Dict[str, Any]]:
        payload = {
            "ui_prefs": ui_prefs,
            "user_query": user_query,
            "location": location,
            "location_name": location_name,
            "taste_profile": taste_profile,
        }

        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        places = [Place.from_dict(item) for item in data.get("results", [])]
        final_prefs = data.get("final_prefs", ui_prefs)
        return places, final_prefs
