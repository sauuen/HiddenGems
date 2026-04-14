from dataclasses import dataclass


@dataclass
class Place:
    name: str
    rating: float
    reviews: int
    distance_km: float
    category: str = "restaurant"
    score: float = 0.0