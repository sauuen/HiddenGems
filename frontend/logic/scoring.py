def calculate_score(place, prefs=None):
    rating_score = place.rating * 20
    review_bonus = max(0, 120 - min(place.reviews, 120)) * 0.18
    rarity_penalty = 0
    chain_penalty = 0

    if place.reviews > 300:
        rarity_penalty = min((place.reviews - 300) * 0.01, 25)

    if place.is_chain:
        chain_penalty = 22

    distance_bonus = max(0, 10 - place.distance_km * 2)

    category_bonus = 0
    price_bonus = 0

    if prefs:
        preferred_categories = prefs.get("preferred_categories", [])
        preferred_price_levels = prefs.get("preferred_price_levels", [])

        if preferred_categories and place.category in preferred_categories:
            category_bonus = 18

        if preferred_price_levels and place.price_level in preferred_price_levels:
            price_bonus = 12

    return round(
        rating_score
        + review_bonus
        + distance_bonus
        + category_bonus
        + price_bonus
        - rarity_penalty
        - chain_penalty,
        2,
    )


def score_places(places, prefs=None):
    for place in places:
        place.score = calculate_score(place, prefs)
    return places