import json
import os

from models.place import Place


class StorageService:
    def __init__(self, file_path="data/favorites.json"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        folder = os.path.dirname(self.file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump([], file)

    def _read_raw(self):
        self._ensure_file()
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _write_raw(self, items):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(items, file, indent=2)

    def get_favorites(self):
        items = self._read_raw()
        return [Place.from_dict(item) for item in items]

    def save_favorite(self, place):
        items = self._read_raw()

        already_exists = any(
            item.get("name", "").lower() == place.name.lower()
            for item in items
        )

        if already_exists:
            return False

        items.append(place.to_dict())
        self._write_raw(items)
        return True

    def remove_favorite(self, place_name):
        items = self._read_raw()
        updated = [
            item for item in items
            if item.get("name", "").lower() != place_name.lower()
        ]

        changed = len(updated) != len(items)
        if changed:
            self._write_raw(updated)

        return changed

    def get_taste_profile(self):
        favorites = self.get_favorites()

        if not favorites:
            return {
                "favorite_categories": [],
                "favorite_price_levels": [],
                "prefers_independent": False,
                "avg_saved_rating": 0.0,
                "summary": "No saved favorites yet.",
            }

        category_counts = {}
        price_counts = {}
        independent_count = 0
        total_rating = 0.0

        for place in favorites:
            category_counts[place.category] = category_counts.get(place.category, 0) + 1
            price_counts[place.price_level] = price_counts.get(place.price_level, 0) + 1

            if not place.is_chain:
                independent_count += 1

            total_rating += float(place.rating or 0)

        favorite_categories = sorted(
            category_counts.keys(),
            key=lambda key: category_counts[key],
            reverse=True,
        )

        favorite_price_levels = sorted(
            price_counts.keys(),
            key=lambda key: price_counts[key],
            reverse=True,
        )

        avg_saved_rating = round(total_rating / len(favorites), 2)
        prefers_independent = independent_count >= max(1, len(favorites) / 2)

        summary_parts = []
        if favorite_categories:
            summary_parts.append(f"Likes {', '.join(favorite_categories[:3])}")
        if favorite_price_levels:
            summary_parts.append(f"Usually saves {', '.join(favorite_price_levels[:2])} places")
        if prefers_independent:
            summary_parts.append("Leans independent over chains")

        summary = " • ".join(summary_parts) if summary_parts else "No strong taste signals yet."

        return {
            "favorite_categories": favorite_categories[:5],
            "favorite_price_levels": favorite_price_levels[:3],
            "prefers_independent": prefers_independent,
            "avg_saved_rating": avg_saved_rating,
            "summary": summary,
        }