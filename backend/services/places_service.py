import math
from typing import Any, Dict, List, Optional

import requests

from config import (
    GOOGLE_PLACES_API_KEY,
    GOOGLE_PLACES_NEARBY_URL,
    GOOGLE_PLACES_TEXT_URL,
)
from models.place import Place


class PlacesService:
    FIELD_MASK = ",".join(
        [
            "places.displayName",
            "places.location",
            "places.rating",
            "places.userRatingCount",
            "places.primaryType",
            "places.primaryTypeDisplayName",
            "places.types",
            "places.priceLevel",
            "places.googleMapsUri",
        ]
    )

    FOOD_TYPES = {
        "restaurant",
        "meal_takeaway",
        "meal_delivery",
        "cafe",
        "coffee_shop",
        "sandwich_shop",
        "bakery",
        "pizza_restaurant",
        "barbecue_restaurant",
        "seafood_restaurant",
        "japanese_restaurant",
        "korean_restaurant",
        "thai_restaurant",
        "indian_restaurant",
        "italian_restaurant",
        "mexican_restaurant",
        "mediterranean_restaurant",
        "vegan_restaurant",
        "vegetarian_restaurant",
        "ramen_restaurant",
        "sushi_restaurant",
        "breakfast_restaurant",
        "brunch_restaurant",
        "fast_food_restaurant",
    }

    BAD_TYPES = {
        "tourist_attraction",
        "event_venue",
        "performing_arts_theater",
        "movie_theater",
        "shopping_mall",
        "department_store",
        "park",
        "museum",
        "lodging",
        "hotel",
        "observation_deck",
        "amusement_center",
        "banquet_hall",
        "conference_center",
        "stadium",
        "arena",
        "art_gallery",
        "historical_landmark",
        "monument",
    }

    BAD_NAME_WORDS = {
        "observatory",
        "museum",
        "pier",
        "mall",
        "hotel",
        "park",
        "stadium",
        "theater",
        "theatre",
        "center",
        "centre",
        "plaza",
        "hall",
        "market",
        "terminal",
        "station",
    }

    CHAIN_WORDS = {
        "starbucks",
        "mcdonald",
        "burger king",
        "subway",
        "kfc",
        "domino",
        "pizza hut",
        "taco bell",
        "dunkin",
        "dunkin'",
        "pret a manger",
        "five guys",
        "shake shack",
        "chipotle",
        "wendy's",
        "wendys",
        "panera",
        "costa coffee",
        "tim hortons",
        "sbarro",
        "le pain quotidien",
        "hard rock cafe",
        "krispy kreme",
        "jollibee",
        "papa john",
    }

    CATEGORY_MAP = {
        "restaurant": "Restaurant",
        "cafe": "Cafe",
        "coffee_shop": "Cafe",
        "bakery": "Cafe",
        "sandwich_shop": "Cafe",
        "pizza_restaurant": "Pizza",
        "japanese_restaurant": "Sushi",
        "sushi_restaurant": "Sushi",
        "ramen_restaurant": "Ramen",
        "korean_restaurant": "Korean",
        "thai_restaurant": "Thai",
        "indian_restaurant": "Indian",
        "italian_restaurant": "Italian",
        "mexican_restaurant": "Mexican",
        "mediterranean_restaurant": "Mediterranean",
        "vegan_restaurant": "Vegan",
        "vegetarian_restaurant": "Vegan",
        "brunch_restaurant": "Brunch",
        "breakfast_restaurant": "Brunch",
        "fast_food_restaurant": "Burgers",
        "meal_takeaway": "Restaurant",
        "meal_delivery": "Restaurant",
    }

    SEARCH_TYPE_MAP = {
        "Sushi": ["sushi_restaurant", "japanese_restaurant", "restaurant"],
        "Ramen": ["ramen_restaurant", "japanese_restaurant", "restaurant"],
        "Cafe": ["cafe", "coffee_shop", "bakery"],
        "Indian": ["indian_restaurant", "restaurant"],
        "Thai": ["thai_restaurant", "restaurant"],
        "Italian": ["italian_restaurant", "pizza_restaurant", "restaurant"],
        "Pizza": ["pizza_restaurant", "restaurant"],
        "Korean": ["korean_restaurant", "restaurant"],
        "Mexican": ["mexican_restaurant", "restaurant"],
        "Mediterranean": ["mediterranean_restaurant", "restaurant"],
        "Vegan": ["vegan_restaurant", "vegetarian_restaurant", "restaurant"],
        "Brunch": ["brunch_restaurant", "breakfast_restaurant", "cafe"],
        "Burgers": ["fast_food_restaurant", "restaurant"],
        "Restaurant": ["restaurant"],
    }

    TEXT_QUERY_MAP = {
        "Sushi": [
            "sushi restaurant",
            "japanese restaurant",
            "sushi takeaway",
        ],
        "Ramen": [
            "ramen restaurant",
            "japanese noodles",
        ],
        "Cafe": [
            "cafe",
            "coffee shop",
            "bakery cafe",
        ],
        "Indian": ["indian restaurant"],
        "Thai": ["thai restaurant"],
        "Italian": ["italian restaurant", "pizza restaurant"],
        "Pizza": ["pizza restaurant"],
        "Korean": ["korean restaurant"],
        "Mexican": ["mexican restaurant"],
        "Mediterranean": ["mediterranean restaurant"],
        "Vegan": ["vegan restaurant", "vegetarian restaurant"],
        "Brunch": ["brunch cafe", "breakfast cafe"],
        "Burgers": ["burger restaurant"],
        "Restaurant": ["restaurant"],
    }

    def get_places(
        self,
        lat: float,
        lng: float,
        radius_km: int = 5,
        max_results: int = 20,
        preferred_categories: Optional[List[str]] = None,
        raw_query: str = "",
        location_name: str = "",
    ) -> List[Place]:
        if not GOOGLE_PLACES_API_KEY:
            print("[PlacesService] Missing GOOGLE_PLACES_API_KEY.")
            return []

        preferred_categories = preferred_categories or []

        text_results = []
        nearby_results = []

        if preferred_categories:
            text_results = self._search_text(
                lat=lat,
                lng=lng,
                radius_km=radius_km,
                max_results=max_results,
                preferred_categories=preferred_categories,
                raw_query=raw_query,
                location_name=location_name,
            )

        nearby_results = self._search_nearby(
            lat=lat,
            lng=lng,
            radius_km=radius_km,
            max_results=max_results,
            preferred_categories=preferred_categories,
        )

        merged = self._merge_places(text_results, nearby_results)

        if preferred_categories:
            merged = self._strong_category_filter(merged, preferred_categories)

        print(f"[PlacesService] Final merged places: {len(merged)}")
        return merged

    def _search_text(
        self,
        lat: float,
        lng: float,
        radius_km: int,
        max_results: int,
        preferred_categories: List[str],
        raw_query: str,
        location_name: str,
    ) -> List[Place]:
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
                "X-Goog-FieldMask": self.FIELD_MASK,
            }

            queries = []

            for cat in preferred_categories:
                for q in self.TEXT_QUERY_MAP.get(cat, []):
                    if location_name:
                        queries.append(f"{q} near {location_name}")
                    else:
                        queries.append(q)

            if raw_query.strip():
                if location_name:
                    queries.append(f"{raw_query.strip()} near {location_name}")
                else:
                    queries.append(raw_query.strip())

            all_places = []

            for query in queries[:4]:
                payload = {
                    "textQuery": query,
                    "pageSize": max(1, min(max_results, 20)),
                    "locationBias": {
                        "circle": {
                            "center": {
                                "latitude": lat,
                                "longitude": lng,
                            },
                            "radius": max(500, min(int(radius_km * 1000), 50000)),
                        }
                    },
                }

                response = requests.post(
                    GOOGLE_PLACES_TEXT_URL,
                    headers=headers,
                    json=payload,
                    timeout=15,
                )

                print(f"[PlacesService][TextSearch] Query='{query}' Status:", response.status_code)
                if not response.ok:
                    print("[PlacesService][TextSearch] Body:", response.text)
                    continue

                data = response.json()
                places_data = data.get("places", [])

                for item in places_data:
                    place = self._convert_api_place(item, user_lat=lat, user_lng=lng)
                    if place:
                        all_places.append(place)

            deduped = self._merge_places(all_places, [])
            print(f"[PlacesService][TextSearch] Loaded {len(deduped)} places.")
            return deduped

        except Exception as exc:
            print(f"[PlacesService][TextSearch] Failed. Error: {exc}")
            return []

    def _search_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: int,
        max_results: int,
        preferred_categories: List[str],
    ) -> List[Place]:
        try:
            radius_m = max(500, min(int(radius_km * 1000), 50000))
            included_types = self._build_included_types(preferred_categories)

            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
                "X-Goog-FieldMask": self.FIELD_MASK,
            }

            payload = {
                "includedTypes": included_types,
                "excludedTypes": [
                    "tourist_attraction",
                    "lodging",
                    "hotel",
                    "park",
                    "museum",
                    "shopping_mall",
                    "movie_theater",
                    "event_venue",
                ],
                "maxResultCount": max(1, min(max_results, 20)),
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lng,
                        },
                        "radius": radius_m,
                    }
                },
            }

            response = requests.post(
                GOOGLE_PLACES_NEARBY_URL,
                headers=headers,
                json=payload,
                timeout=15,
            )

            print("[PlacesService][Nearby] Status:", response.status_code)
            if not response.ok:
                print("[PlacesService][Nearby] Body:", response.text)

            response.raise_for_status()

            data = response.json()
            places_data = data.get("places", [])

            places: List[Place] = []
            for item in places_data:
                place = self._convert_api_place(item, user_lat=lat, user_lng=lng)
                if place:
                    places.append(place)

            print(f"[PlacesService][Nearby] Loaded {len(places)} places.")
            return places

        except Exception as exc:
            print(f"[PlacesService][Nearby] Failed. Error: {exc}")
            return []

    def _merge_places(self, primary: List[Place], secondary: List[Place]) -> List[Place]:
        merged = []
        seen = set()

        for place in primary + secondary:
            key = place.name.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(place)

        return merged

    def _build_included_types(self, preferred_categories: List[str]) -> List[str]:
        if not preferred_categories:
            return ["restaurant", "cafe"]

        included = []
        for category in preferred_categories:
            for place_type in self.SEARCH_TYPE_MAP.get(category, []):
                if place_type not in included:
                    included.append(place_type)

        return included or ["restaurant", "cafe"]

    def _strong_category_filter(self, places: List[Place], preferred_categories: List[str]) -> List[Place]:
        scored = []

        for p in places:
            category_score = 0
            lower_name = p.name.lower()
            lower_category = (p.category or "").lower()

            if "Sushi" in preferred_categories:
                if lower_category == "sushi":
                    category_score += 5
                if "sushi" in lower_name:
                    category_score += 4
                if "japan" in lower_name or "japanese" in lower_name:
                    category_score += 3
                if "japanese" in lower_category:
                    category_score += 3

            if "Ramen" in preferred_categories:
                if lower_category == "ramen":
                    category_score += 5
                if "ramen" in lower_name:
                    category_score += 4

            if "Cafe" in preferred_categories:
                if lower_category == "cafe":
                    category_score += 5
                if any(word in lower_name for word in ["cafe", "coffee", "espresso"]):
                    category_score += 3

            if "Pizza" in preferred_categories:
                if lower_category == "pizza":
                    category_score += 5
                if "pizza" in lower_name:
                    category_score += 3

            if "Thai" in preferred_categories and ("thai" in lower_name or lower_category == "thai"):
                category_score += 5

            if "Indian" in preferred_categories and ("indian" in lower_name or lower_category == "indian"):
                category_score += 5

            if "Italian" in preferred_categories and ("italian" in lower_name or lower_category == "italian"):
                category_score += 5

            if "Korean" in preferred_categories and ("korean" in lower_name or lower_category == "korean"):
                category_score += 5

            if "Mexican" in preferred_categories and ("mexican" in lower_name or lower_category == "mexican"):
                category_score += 5

            if "Vegan" in preferred_categories and ("vegan" in lower_name or lower_category == "vegan"):
                category_score += 5

            scored.append((category_score, p))

        scored.sort(key=lambda item: item[0], reverse=True)
        strong = [p for score, p in scored if score > 0]
        return strong if strong else places

    def _convert_api_place(
        self,
        item: Dict[str, Any],
        user_lat: float,
        user_lng: float,
    ) -> Optional[Place]:
        try:
            name = self._extract_text_field(item.get("displayName")) or "Unknown Place"
            lower_name = name.lower()

            primary_type = str(item.get("primaryType", "")).strip()
            types = item.get("types", []) or []

            all_types = set()
            if primary_type:
                all_types.add(primary_type)
            for t in types:
                if isinstance(t, str):
                    all_types.add(t)

            if not any(t in self.FOOD_TYPES for t in all_types):
                return None

            if any(t in self.BAD_TYPES for t in all_types):
                return None

            if any(word in lower_name for word in self.BAD_NAME_WORDS):
                if not any(t in self.FOOD_TYPES for t in all_types if t != "restaurant"):
                    return None

            location = item.get("location", {})
            place_lat = location.get("latitude")
            place_lng = location.get("longitude")

            if place_lat is None or place_lng is None:
                return None

            rating = float(item.get("rating", 0.0) or 0.0)
            reviews = int(item.get("userRatingCount", 0) or 0)

            category = self._map_category(primary_type, types, name)
            price_level = self._map_price_level(item.get("priceLevel"))
            maps_url = str(item.get("googleMapsUri", "") or "")
            is_chain = self._is_chain(name)

            distance_km = round(
                self._haversine_km(user_lat, user_lng, place_lat, place_lng),
                1,
            )

            return Place(
                name=name,
                rating=rating,
                reviews=reviews,
                distance_km=distance_km,
                category=category,
                price_level=price_level,
                maps_url=maps_url,
                lat=float(place_lat),
                lon=float(place_lng),
                is_chain=is_chain,
            )
        except Exception:
            return None

    def _is_chain(self, name: str) -> bool:
        lower_name = name.lower()
        return any(chain in lower_name for chain in self.CHAIN_WORDS)

    def _map_category(self, primary_type: str, types: List[Any], name: str) -> str:
        lower_name = (name or "").lower()

        if "sushi" in lower_name or "japan" in lower_name or "japanese" in lower_name:
            return "Sushi"
        if "ramen" in lower_name:
            return "Ramen"
        if "pizza" in lower_name:
            return "Pizza"
        if "cafe" in lower_name or "coffee" in lower_name:
            return "Cafe"

        if primary_type in self.CATEGORY_MAP:
            return self.CATEGORY_MAP[primary_type]

        for t in types or []:
            if isinstance(t, str) and t in self.CATEGORY_MAP:
                return self.CATEGORY_MAP[t]

        return "Restaurant"

    def _extract_text_field(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return str(value.get("text", "")).strip()
        return ""

    def _map_price_level(self, value: Any) -> str:
        if not value:
            return "$$"

        value = str(value).upper()

        mapping = {
            "PRICE_LEVEL_FREE": "$",
            "PRICE_LEVEL_INEXPENSIVE": "$",
            "PRICE_LEVEL_MODERATE": "$$",
            "PRICE_LEVEL_EXPENSIVE": "$$$",
            "PRICE_LEVEL_VERY_EXPENSIVE": "$$$",
        }
        return mapping.get(value, "$$")

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c