from copy import deepcopy

from config import DEFAULT_PREFS, LLM_MAX_CANDIDATES
from services.gps_service import GPSService
from services.places_service import PlacesService
from services.llm_service import LLMService
from services.storage_service import StorageService
from logic.filtering import filter_places


class RecommendationEngine:
    _shared_gps_service = GPSService()
    _shared_places_service = PlacesService()
    _shared_llm_service = LLMService()
    _shared_storage_service = StorageService()

    def __init__(self):
        self.gps_service = self._shared_gps_service
        self.places_service = self._shared_places_service
        self.llm_service = self._shared_llm_service
        self.storage_service = self._shared_storage_service

    def _build_final_prefs(self, ui_prefs, user_query):
        final_prefs = deepcopy(DEFAULT_PREFS)

        for key, value in ui_prefs.items():
            final_prefs[key] = value

        llm_updates = self.llm_service.parse_query(user_query)

        for key, value in llm_updates.items():
            final_prefs[key] = value

        return final_prefs

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

    def get_recommendations(self, ui_prefs, user_query=""):
        location = self.gps_service.get_location()
        location_name = self.gps_service.get_location_name()
        final_prefs = self._build_final_prefs(ui_prefs, user_query)
        taste_profile = self.get_taste_profile()

        preferred_categories = final_prefs.get("preferred_categories", [])

        places = self.places_service.get_places(
            location["lat"],
            location["lng"],
            radius_km=final_prefs["radius_km"],
            max_results=20,
            preferred_categories=preferred_categories,
            raw_query=user_query,
            location_name=location_name,
        )

        filtered = filter_places(places, final_prefs)

        candidates = filtered[:LLM_MAX_CANDIDATES]
        ranked = self.llm_service.rank_places(
            user_query=user_query,
            final_prefs=final_prefs,
            places=candidates,
            taste_profile=taste_profile,
        )

        for place in ranked:
            if not place.reason:
                place.reason = self.llm_service.explain_place(place, final_prefs)

        return ranked, final_prefs