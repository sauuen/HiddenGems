def passes_filters(place, filters_data):
    if place.rating < filters_data["min_rating"]:
        return False
    if place.reviews < filters_data["min_reviews"]:
        return False
    if place.distance_km > filters_data["radius_km"]:
        return False
    return True


def calculate_score(place):
    """
    Simple hidden gem score:
    higher rating good
    fewer reviews slightly better
    closer distance better
    """
    rating_points = place.rating * 20
    review_bonus = max(0, 120 - place.reviews) * 0.2
    distance_bonus = max(0, 10 - place.distance_km * 2)
    return round(rating_points + review_bonus + distance_bonus, 2)