from copy import deepcopy
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import DEFAULT_PREFS, GOOGLE_PLACES_API_KEY, OPENAI_API_KEY, LLM_MAX_CANDIDATES
from logic.filtering import filter_places
from services.llm_service import LLMService
from services.places_service import PlacesService


class LocationPayload(BaseModel):
    lat: float
    lng: float


class RecommendationRequest(BaseModel):
    ui_prefs: Dict[str, Any] = Field(default_factory=dict)
    user_query: str = ""
    location: LocationPayload
    location_name: str = "Current location"
    taste_profile: Optional[Dict[str, Any]] = None


app = FastAPI(title="Hidden Gems Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

places_service = PlacesService()
llm_service = LLMService()


def build_final_prefs(ui_prefs: Dict[str, Any], user_query: str) -> Dict[str, Any]:
    final_prefs = deepcopy(DEFAULT_PREFS)
    final_prefs.update(ui_prefs or {})

    # Query parsing is backend-side so the frontend does not need the LLM service or keys.
    llm_updates = llm_service.parse_query(user_query or "")
    final_prefs.update(llm_updates or {})
    return final_prefs


@app.get("/api/status")
def status():
    return {
        "backend": "online",
        "places_enabled": bool(GOOGLE_PLACES_API_KEY),
        "llm_enabled": bool(OPENAI_API_KEY),
    }


@app.post("/api/recommendations")
def recommendations(request: RecommendationRequest):
    final_prefs = build_final_prefs(request.ui_prefs, request.user_query)
    preferred_categories: List[str] = final_prefs.get("preferred_categories", []) or []
    taste_profile = request.taste_profile or {}

    places = places_service.get_places(
        request.location.lat,
        request.location.lng,
        radius_km=int(final_prefs.get("radius_km", 8)),
        max_results=20,
        preferred_categories=preferred_categories,
        raw_query=request.user_query or "",
        location_name=request.location_name or "Current location",
    )

    filtered = filter_places(places, final_prefs)
    candidates = filtered[:LLM_MAX_CANDIDATES]

    ranked = llm_service.rank_places(
        user_query=request.user_query or "",
        final_prefs=final_prefs,
        places=candidates,
        taste_profile=taste_profile,
    )

    for place in ranked:
        if not place.reason:
            place.reason = llm_service.explain_place(place, final_prefs)

    return {
        "results": [place.to_dict() for place in ranked],
        "final_prefs": final_prefs,
    }
