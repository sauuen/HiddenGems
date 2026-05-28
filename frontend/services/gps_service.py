from geopy.geocoders import Nominatim


class GPSService:
    def __init__(self):
        self.selected_location = {
            "name": "Oslo",
            "lat": 59.9139,
            "lng": 10.7522,
        }

        self.saved_locations = {
            "Oslo": {"lat": 59.9139, "lng": 10.7522},
            "New York": {"lat": 40.7128, "lng": -74.0060},
            "London": {"lat": 51.5072, "lng": -0.1276},
            "Tokyo": {"lat": 35.6762, "lng": 139.6503},
            "Paris": {"lat": 48.8566, "lng": 2.3522},
            "Hamar": {"lat": 60.7945, "lng": 11.06798},
        }

        self.geocoder = Nominatim(user_agent="hidden_gems_app")

    def get_location(self):
        return {
            "lat": self.selected_location["lat"],
            "lng": self.selected_location["lng"],
        }

    def get_location_name(self):
        return self.selected_location["name"]

    def set_named_location(self, name):
        if name in self.saved_locations:
            coords = self.saved_locations[name]
            self.selected_location = {
                "name": name,
                "lat": coords["lat"],
                "lng": coords["lng"],
            }
            return True
        return False

    def set_custom_location(self, name, lat, lng):
        try:
            lat = float(lat)
            lng = float(lng)
        except Exception:
            return False

        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return False

        clean_name = (name or f"{lat},{lng}").strip() or f"{lat},{lng}"

        self.selected_location = {
            "name": clean_name,
            "lat": lat,
            "lng": lng,
        }
        return True

    def _try_parse_coordinates(self, text):
        parts = [p.strip() for p in text.split(",")]
        if len(parts) != 2:
            return None

        try:
            lat = float(parts[0])
            lng = float(parts[1])
        except Exception:
            return None

        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return None

        return lat, lng

    def set_location_from_input(self, text):
        text = (text or "").strip()
        if not text:
            return False, "Enter a city, address, or lat,lng"

        if text in self.saved_locations:
            self.set_named_location(text)
            return True, f"Location set to {text}"

        lowered = text.lower()
        for name in self.saved_locations:
            if name.lower() == lowered:
                self.set_named_location(name)
                return True, f"Location set to {name}"

        # Only treat as coordinates if both values are actually numeric
        coords = self._try_parse_coordinates(text)
        if coords is not None:
            lat, lng = coords
            success = self.set_custom_location(text, lat, lng)
            if success:
                return True, f"Location set to {text}"
            return False, "Coordinates out of range"

        # Otherwise geocode as address/place text
        try:
            location = self.geocoder.geocode(text, timeout=10)
            if not location:
                return False, "Location not found"

            display_name = text

            self.selected_location = {
                "name": display_name,
                "lat": float(location.latitude),
                "lng": float(location.longitude),
            }
            return True, f"Location set to {display_name}"

        except Exception:
            return False, "Geocoding failed. Try a city, address, or lat,lng"

    def get_available_location_names(self):
        return list(self.saved_locations.keys())