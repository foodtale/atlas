import logging

import httpx

from atlas.models.config import Config
from atlas.services.base import BaseService

logger = logging.getLogger(__name__)


class GoogleMapCitySearchService(BaseService):
    """
    Search cities using Google Places Text Search (New) API.

    Extracts the locality component from each result and returns a deduplicated
    list of city name strings.

    Usage:
        result, error = GoogleMapCitySearchService.call(query="Hyd")

        if not error:
            cities = result["cities"]
            # ["Hyderabad"]
    """

    FIELD_MASK = (
        "places.id,"
        "places.displayName,"
        "places.addressComponents"
    )

    def perform(self):
        query = self.context["query"]
        limit = self.context.get("limit", 5)

        api_key = Config.get("GOOGLE_PLACES_API_KEY")
        if not api_key:
            self.fail(message="Google Places API is not configured.")

        try:
            response = httpx.post(
                Config.get("GOOGLE_PLACES_API_BASE_URL"),
                json={
                    "textQuery": query,
                    "pageSize": limit,
                },
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": self.FIELD_MASK,
                },
                timeout=5,
            )

            response.raise_for_status()
            payload = response.json()

        except httpx.HTTPError as exc:
            logger.exception("Google city search failed")
            self.fail(message=f"Could not reach Google Places. {exc}")

        cities = []
        for place in payload.get("places", []):
            city = self._get_locality(place)
            if city and city not in cities:
                cities.append(city)

        self.result["cities"] = cities

    @staticmethod
    def _get_locality(place):
        for component in place.get("addressComponents", []):
            if "locality" in component.get("types", []):
                return component.get("longText")
        return None
