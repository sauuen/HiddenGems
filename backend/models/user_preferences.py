from dataclasses import dataclass


@dataclass
class UserPreferences:
    min_rating: float = 4.0
    min_reviews: int = 10
    max_reviews: int = 250
    radius_km: int = 5

    def to_dict(self):
        return {
            "min_rating": self.min_rating,
            "min_reviews": self.min_reviews,
            "max_reviews": self.max_reviews,
            "radius_km": self.radius_km,
        }