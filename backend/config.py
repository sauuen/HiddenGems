import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Hidden Gems"

DEFAULT_MIN_RATING = 3.0
DEFAULT_MIN_REVIEWS = 0
DEFAULT_MAX_REVIEWS = 999999
DEFAULT_RADIUS_KM = 8
DEFAULT_SORT_MODE = "hidden_gem"

DEFAULT_PREFS = {
    "min_rating": DEFAULT_MIN_RATING,
    "min_reviews": DEFAULT_MIN_REVIEWS,
    "max_reviews": DEFAULT_MAX_REVIEWS,
    "radius_km": DEFAULT_RADIUS_KM,
    "sort_mode": DEFAULT_SORT_MODE,
}

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
GOOGLE_PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"
GOOGLE_PLACES_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"

LLM_MAX_CANDIDATES = 12

print("OPENAI_API_KEY FOUND:", bool(OPENAI_API_KEY))
print("GOOGLE_PLACES_API_KEY FOUND:", bool(GOOGLE_PLACES_API_KEY))