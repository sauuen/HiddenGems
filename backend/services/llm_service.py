import json
import time
import hashlib

from config import OPENAI_API_KEY, OPENAI_MODEL

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


class LLMService:
    CATEGORY_KEYWORDS = {
        "sushi": "Sushi",
        "ramen": "Ramen",
        "burger": "Burgers",
        "burgers": "Burgers",
        "cafe": "Cafe",
        "coffee": "Cafe",
        "indian": "Indian",
        "thai": "Thai",
        "italian": "Italian",
        "pizza": "Pizza",
        "korean": "Korean",
        "pho": "Vietnamese",
        "vietnamese": "Vietnamese",
        "brunch": "Brunch",
        "vegan": "Vegan",
        "mexican": "Mexican",
        "mediterranean": "Mediterranean",
        "noodles": "Noodles",
    }

    CHEAP_WORDS = ["cheap", "budget", "affordable", "low cost", "inexpensive"]
    EXPENSIVE_WORDS = ["fancy", "expensive", "upscale", "premium", "nice dinner", "high end"]

    def __init__(self):
        self.client = None
        self.rank_cache = {}
        self.rate_limited_until = 0.0

        if OpenAI and OPENAI_API_KEY:
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    max_retries=0,
                )
            except Exception:
                self.client = None

    def parse_query(self, text):
        """
        Local parsing only.

        This keeps the app fast and avoids burning one extra LLM call.
        The LLM remains the main part because ranking is still LLM-driven.
        """
        return self._fallback_parse_query(text)

    def rank_places(self, user_query, final_prefs, places, taste_profile=None):
        """
        Main LLM ranking step.

        Optimized to avoid rate-limit problems:
        - 0 calls if no places
        - 0 calls if only 1 place
        - 0 calls if temporarily rate-limited
        - cached results for repeated searches
        - 1 LLM call max per search
        """
        if not places:
            return places

        taste_profile = taste_profile or {}

        if len(places) == 1:
            single = places[0]
            single.score = round(float(single.rating) * 20, 2)
            single.reason = self._fallback_explain_place(single, final_prefs, taste_profile)
            return [single]

        cache_key = self._make_rank_cache_key(user_query, final_prefs, places, taste_profile)
        if cache_key in self.rank_cache:
            return self._clone_ranked_places(places, self.rank_cache[cache_key])

        if self._is_rate_limited() or not self.client:
            return self._fallback_rank_places(user_query, final_prefs, places, taste_profile)

        try:
            candidates_payload = []
            for idx, place in enumerate(places, start=1):
                candidates_payload.append(
                    {
                        "id": idx,
                        "name": place.name,
                        "category": place.category,
                        "rating": place.rating,
                        "reviews": place.reviews,
                        "distance_km": place.distance_km,
                        "price_level": place.price_level,
                        "is_chain": place.is_chain,
                    }
                )

            prompt = (
                "You are the main recommendation engine for a restaurant discovery app called Hidden Gems.\n"
                "Your job is to rank nearby restaurant candidates.\n\n"
                "Ranking rules:\n"
                "- Match the user's request closely.\n"
                "- Prefer places that feel like hidden gems when appropriate.\n"
                "- Prefer independent places over chains when possible.\n"
                "- Use the user's taste profile from saved favorites as a personalization signal.\n"
                "- Do NOT invent facts.\n"
                "- Use ONLY the provided candidate data.\n\n"
                "Return ONLY valid JSON in this format:\n"
                "{\n"
                '  "ranked": [\n'
                '    {"id": 2, "score": 97, "reason": "..."},\n'
                '    {"id": 1, "score": 90, "reason": "..."}\n'
                "  ]\n"
                "}\n\n"
                f"User query: {user_query}\n"
                f"Preferences: {json.dumps(final_prefs, ensure_ascii=False)}\n"
                f"Taste profile: {json.dumps(taste_profile, ensure_ascii=False)}\n"
                f"Candidates: {json.dumps(candidates_payload, ensure_ascii=False)}\n"
            )

            response = self.client.responses.create(
                model=OPENAI_MODEL,
                input=prompt,
            )

            raw = (response.output_text or "").strip()
            parsed = json.loads(raw)

            ranked = parsed.get("ranked", [])
            if not isinstance(ranked, list):
                return self._fallback_rank_places(user_query, final_prefs, places, taste_profile)

            id_to_place = {idx: place for idx, place in enumerate(places, start=1)}
            reranked = []

            for item in ranked:
                if not isinstance(item, dict):
                    continue

                item_id = item.get("id")
                if item_id not in id_to_place:
                    continue

                place = id_to_place[item_id]
                score = item.get("score", place.score)
                reason = item.get("reason", "")

                try:
                    place.score = float(score)
                except Exception:
                    pass

                if isinstance(reason, str) and reason.strip():
                    place.reason = reason.strip()
                else:
                    place.reason = self._fallback_explain_place(place, final_prefs, taste_profile)

                reranked.append(place)

            if reranked:
                seen = {id(p) for p in reranked}
                leftovers = [p for p in places if id(p) not in seen]
                leftovers = self._fallback_rank_places(user_query, final_prefs, leftovers, taste_profile)
                final_ranked = reranked + leftovers

                self.rank_cache[cache_key] = [
                    {
                        "name": p.name,
                        "score": p.score,
                        "reason": p.reason,
                    }
                    for p in final_ranked
                ]
                return final_ranked

        except Exception as exc:
            if "429" in str(exc):
                self.rate_limited_until = time.time() + 120
            return self._fallback_rank_places(user_query, final_prefs, places, taste_profile)

        return self._fallback_rank_places(user_query, final_prefs, places, taste_profile)

    def explain_place(self, place, final_prefs=None):
        if place.reason:
            return place.reason
        return self._fallback_explain_place(place, final_prefs, None)

    def _is_rate_limited(self):
        return time.time() < self.rate_limited_until

    def _make_rank_cache_key(self, user_query, final_prefs, places, taste_profile):
        payload = {
            "user_query": user_query,
            "final_prefs": final_prefs,
            "taste_profile": taste_profile,
            "places": [
                {
                    "name": p.name,
                    "category": p.category,
                    "rating": p.rating,
                    "reviews": p.reviews,
                    "distance_km": p.distance_km,
                    "price_level": p.price_level,
                    "is_chain": p.is_chain,
                }
                for p in places
            ],
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _clone_ranked_places(self, places, cached_items):
        by_name = {p.name: p for p in places}
        ranked = []

        for item in cached_items:
            place = by_name.get(item["name"])
            if not place:
                continue
            place.score = item["score"]
            place.reason = item["reason"]
            ranked.append(place)

        leftovers = [p for p in places if p.name not in {r.name for r in ranked}]
        return ranked + leftovers

    def _fallback_parse_query(self, text):
        text = (text or "").strip().lower()
        updates = {}

        if "very strict" in text:
            updates["min_rating"] = 4.7
            updates["min_reviews"] = 40
            updates["max_reviews"] = 100
        elif "strict" in text:
            updates["min_rating"] = 4.5
            updates["min_reviews"] = 25
            updates["max_reviews"] = 150
        elif "relaxed" in text or "casual" in text:
            updates["min_rating"] = 4.0
            updates["min_reviews"] = 5
            updates["max_reviews"] = 300

        if "super close" in text or "very close" in text:
            updates["radius_km"] = 2
        elif "nearby" in text or "close" in text or "walking distance" in text:
            updates["radius_km"] = 3

        if "hidden gem" in text or "underrated" in text or "not touristy" in text:
            updates["max_reviews"] = min(updates.get("max_reviews", 999999), 120)
            updates["sort_mode"] = "hidden_gem"
            updates["prefer_independent"] = True
            updates["avoid_touristy"] = True

        if "popular" in text or "well known" in text:
            updates["min_reviews"] = max(updates.get("min_reviews", 0), 50)

        if "small place" in text or "local spot" in text or "hole in the wall" in text:
            updates["max_reviews"] = min(updates.get("max_reviews", 999999), 90)
            updates["prefer_independent"] = True

        if "highly rated" in text or "top rated" in text or "best rated" in text:
            updates["min_rating"] = max(updates.get("min_rating", 0), 4.6)

        if "good reviews" in text:
            updates["min_reviews"] = max(updates.get("min_reviews", 0), 20)

        if "closest" in text or "nearest" in text:
            updates["sort_mode"] = "closest"
        elif "highest rated" in text or "best rated" in text or "top rated" in text:
            updates["sort_mode"] = "highest_rated"

        categories = []
        for keyword, category in self.CATEGORY_KEYWORDS.items():
            if keyword in text and category not in categories:
                categories.append(category)
        if categories:
            updates["preferred_categories"] = categories

        desired_prices = []
        if any(word in text for word in self.CHEAP_WORDS):
            desired_prices = ["$"]
        if any(word in text for word in self.EXPENSIVE_WORDS):
            desired_prices = ["$$$", "$$"]
        if "mid range" in text or "midrange" in text:
            desired_prices = ["$$"]
        if desired_prices:
            updates["preferred_price_levels"] = desired_prices

        return updates

    def _fallback_rank_places(self, user_query, final_prefs, places, taste_profile=None):
        preferred_categories = final_prefs.get("preferred_categories", [])
        preferred_prices = final_prefs.get("preferred_price_levels", [])
        sort_mode = final_prefs.get("sort_mode", "hidden_gem")
        prefer_independent = final_prefs.get("prefer_independent", False)

        taste_profile = taste_profile or {}
        taste_categories = taste_profile.get("favorite_categories", [])
        taste_prices = taste_profile.get("favorite_price_levels", [])
        taste_prefers_independent = taste_profile.get("prefers_independent", False)

        ranked = []

        for place in places:
            score = 0.0

            score += float(place.rating) * 20
            score += max(0, 120 - min(int(place.reviews), 120)) * 0.18
            score += max(0, 10 - float(place.distance_km) * 2)

            if preferred_categories and place.category in preferred_categories:
                score += 18

            if preferred_prices and place.price_level in preferred_prices:
                score += 12

            if place.category in taste_categories:
                score += 10

            if place.price_level in taste_prices:
                score += 6

            if prefer_independent and not place.is_chain:
                score += 20

            if taste_prefers_independent and not place.is_chain:
                score += 12

            if place.is_chain:
                score -= 22

            if sort_mode == "closest":
                score += max(0, 20 - float(place.distance_km) * 5)

            if sort_mode == "highest_rated":
                score += float(place.rating) * 8

            place.score = round(score, 2)
            place.reason = self._fallback_explain_place(place, final_prefs, taste_profile)
            ranked.append(place)

        ranked.sort(key=lambda p: p.score, reverse=True)
        return ranked

    def _fallback_explain_place(self, place, final_prefs=None, taste_profile=None):
        preferred_categories = []
        preferred_prices = []
        sort_mode = "hidden_gem"

        if final_prefs:
            preferred_categories = final_prefs.get("preferred_categories", [])
            preferred_prices = final_prefs.get("preferred_price_levels", [])
            sort_mode = final_prefs.get("sort_mode", "hidden_gem")

        taste_profile = taste_profile or {}
        taste_categories = taste_profile.get("favorite_categories", [])
        taste_prefers_independent = taste_profile.get("prefers_independent", False)

        if place.category in taste_categories[:3] and not place.is_chain:
            return "Fits your saved taste profile and looks like an independent spot."

        if place.is_chain:
            return "Matches your filters, but it looks like a well-known chain."

        if preferred_categories and preferred_prices:
            if place.category in preferred_categories and place.price_level in preferred_prices:
                return (
                    f"Matches your search for {place.category.lower()} "
                    f"and your preferred price range."
                )

        if preferred_categories and place.category in preferred_categories:
            return f"Matches your search for {place.category.lower()} and fits your filters."

        if preferred_prices and place.price_level in preferred_prices:
            return "Fits the price range you asked for and still matches your hidden gem filters."

        if taste_prefers_independent and not place.is_chain:
            return "Looks aligned with your saved preference for more independent places."

        if sort_mode == "closest":
            return "One of the closest matches that still fits your filters."

        if sort_mode == "highest_rated":
            return "Ranks highly for rating while still matching your search."

        if place.rating >= 4.7 and place.reviews <= 60:
            return "Excellent ratings and still not too well known."

        if place.distance_km <= 1.0 and place.reviews <= 80:
            return "Very close by and still feels like a local find."

        if place.reviews <= 40:
            return "Strong ratings with fewer reviews, which makes it feel like a hidden gem."

        if place.rating >= 4.6:
            return "High quality spot that matches your filters well."

        return "Matches your hidden gem settings."