from dataclasses import dataclass, field


@dataclass
class Place:
    name: str
    rating: float
    reviews: int
    distance_km: float
    category: str = "Restaurant"
    price_level: str = "$$"
    score: float = 0.0
    reason: str = field(default="")
    maps_url: str = field(default="")
    lat: float = 0.0
    lon: float = 0.0
    is_chain: bool = False

    def to_dict(self):
        return {
            "name": self.name,
            "rating": self.rating,
            "reviews": self.reviews,
            "distance_km": self.distance_km,
            "category": self.category,
            "price_level": self.price_level,
            "score": self.score,
            "reason": self.reason,
            "maps_url": self.maps_url,
            "lat": self.lat,
            "lon": self.lon,
            "is_chain": self.is_chain,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            rating=data.get("rating", 0.0),
            reviews=data.get("reviews", 0),
            distance_km=data.get("distance_km", 0.0),
            category=data.get("category", "Restaurant"),
            price_level=data.get("price_level", "$$"),
            score=data.get("score", 0.0),
            reason=data.get("reason", ""),
            maps_url=data.get("maps_url", ""),
            lat=data.get("lat", 0.0),
            lon=data.get("lon", 0.0),
            is_chain=bool(data.get("is_chain", False)),
        )