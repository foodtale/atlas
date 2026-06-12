import logging

import httpx

from atlas.models.config import Config
from atlas.services.base import BaseService

logger = logging.getLogger(__name__)


class GoogleMapPlaceDetailService(BaseService):
    """
    Fetch a single place by place_id using Google Places Details (New) API.

    Usage:
        result, error = GoogleMapPlaceDetailService.call(
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4"
        )
    """

    FIELD_MASK = (
        "id,"
        "displayName,"
        "formattedAddress,"
        "location,"
        "addressComponents"
    )

    def perform(self):
        place_id = self.context["place_id"]

        api_key = Config.get("GOOGLE_PLACES_API_KEY")
        if not api_key:
            self.fail(message="Google Places API is not configured.")

        base_url = Config.get("GOOGLE_PLACES_DETAIL_BASE_URL")
        url = f"{base_url}/{place_id}"

        try:
            response = httpx.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": self.FIELD_MASK,
                },
                timeout=5,
            )

            response.raise_for_status()
            place = response.json()

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self.fail(message="Place not found.")
            logger.exception("Google Places detail fetch failed")
            self.fail(message=f"Could not reach Google Places. {exc}")

        except httpx.HTTPError as exc:
            logger.exception("Google Places detail fetch failed")
            self.fail(message=f"Could not reach Google Places. {exc}")

        self.result["place"] = self._normalize_place(place)

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
            "state": cls._get_component(place, "administrative_area_level_1"),
            "country": cls._get_component(place, "country"),
            "postal_code": cls._get_component(place, "postal_code"),
        }

    @staticmethod
    def _get_component(place, component_type):
        for component in place.get("addressComponents", []):
            if component_type in component.get("types", []):
                return component.get("longText")
        return None
