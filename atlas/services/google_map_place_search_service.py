import logging

import httpx

from atlas.models.config import Config
from atlas.services.base import BaseService

logger = logging.getLogger(__name__)


class GoogleMapPlaceSearchService(BaseService):
    """
    Search places using Google Places Text Search (New) API.

    Usage:
        result, error = GoogleMapPlaceSearchService.call(
            query="Pizza Hut Bangalore"
        )
    """

    FIELD_MASK = (
        "places.id,"
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.addressComponents"
    )

    def perform(self):
        query = self.context["query"]
        limit = self.context.get("limit", 10)

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
            logger.exception("Google Places search failed")
            self.fail(message=f"Could not reach Google Places. {exc}")

        self.result["places"] = [
            self._normalize_place(place) for place in payload.get("places", [])
        ]

    @classmethod
    def _normalize_place(cls, place):
        location = place.get("location", {})

        return {
            "place_id": place.get("id"),
            "name": place.get("displayName", {}).get("text"),
            "address": place.get("formattedAddress"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "city": cls._get_component(place, "locality"),
            "state": cls._get_component(
                place,
                "administrative_area_level_1",
            ),
            "country": cls._get_component(place, "country"),
            "postal_code": cls._get_component(
                place,
                "postal_code",
            ),
        }

    @staticmethod
    def _get_component(place, component_type):
        """
        Extract a value from Google's addressComponents.
        """

        for component in place.get("addressComponents", []):
            if component_type in component.get("types", []):
                return component.get("longText")

        return None
