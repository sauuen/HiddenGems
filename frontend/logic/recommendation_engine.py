from copy import deepcopy

from config import DEFAULT_PREFS
from services.api_client import ApiClient
from services.gps_service import GPSService
from services.storage_service import StorageService


class RecommendationEngine:
    _shared_gps_service = GPSService()
    _shared_storage_service = StorageService()
    _shared_api_client = ApiClient()

    def __init__(self):
        self.gps_service = self._shared_gps_service
        self.storage_service = self._shared_storage_service
        self.api_client = self._shared_api_client

    def get_current_location_name(self):
        return self.gps_service.get_location_name()

    def get_available_location_names(self):
        return self.gps_service.get_available_location_names()

    def set_named_location(self, name):
        return self.gps_service.set_named_location(name)

    def set_location_from_input(self, text):
        return self.gps_service.set_location_from_input(text)

    def get_taste_profile(self):
        return self.storage_service.get_taste_profile()

    def backend_status(self):
        return self.api_client.get_status()

    def get_recommendations(self, ui_prefs, user_query=""):
        location = self.gps_service.get_location()
        location_name = self.gps_service.get_location_name()
        taste_profile = self.get_taste_profile()

        try:
            return self.api_client.get_recommendations(
                ui_prefs=ui_prefs,
                user_query=user_query,
                location=location,
                location_name=location_name,
                taste_profile=taste_profile,
            )
        except Exception as exc:
            print(f"[Frontend] Backend request failed: {exc}")
            fallback_prefs = deepcopy(DEFAULT_PREFS)
            fallback_prefs.update(ui_prefs or {})
            return [], fallback_prefs
