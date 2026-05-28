def _matches_preferred_category(place, preferred_categories):
    if not preferred_categories:
        return True

    category = (place.category or "").strip()
    lower_name = (place.name or "").lower()

    for preferred in preferred_categories:
        if category == preferred:
            return True

        if preferred == "Sushi":
            if any(word in lower_name for word in ["sushi", "japan", "japanese"]):
                return True

        elif preferred == "Ramen":
            if "ramen" in lower_name:
                return True

        elif preferred == "Cafe":
            if any(word in lower_name for word in ["cafe", "coffee", "espresso", "bakery"]):
                return True

        elif preferred == "Pizza":
            if "pizza" in lower_name:
                return True

        elif preferred == "Thai":
            if "thai" in lower_name:
                return True

        elif preferred == "Indian":
            if "indian" in lower_name:
                return True

        elif preferred == "Italian":
            if "italian" in lower_name:
                return True

        elif preferred == "Korean":
            if "korean" in lower_name:
                return True

        elif preferred == "Mexican":
            if "mexican" in lower_name:
                return True

        elif preferred == "Vegan":
            if "vegan" in lower_name or "vegetarian" in lower_name:
                return True

        elif preferred == "Brunch":
            if any(word in lower_name for word in ["brunch", "breakfast"]):
                return True

        elif preferred == "Burgers":
            if any(word in lower_name for word in ["burger", "burgers"]):
                return True

    return False


def filter_places(places, prefs):
    filtered = []
    preferred_categories = prefs.get("preferred_categories", [])
    preferred_price_levels = prefs.get("preferred_price_levels", [])

    for place in places:
        rating = float(place.rating or 0)
        reviews = int(place.reviews or 0)
        distance_km = float(place.distance_km or 0)

        if rating < prefs["min_rating"]:
            continue

        if reviews < prefs["min_reviews"]:
            continue

        if distance_km > prefs["radius_km"]:
            continue

        if preferred_categories and not _matches_preferred_category(place, preferred_categories):
            continue

        if preferred_price_levels and place.price_level not in preferred_price_levels:
            continue

        filtered.append(place)

    return filtered