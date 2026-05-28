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

# Frontend only knows where the backend is. It never stores API keys.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
