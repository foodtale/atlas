from django.db.models import Q

from atlas.models.outlet import Outlet
from atlas.services.base import BaseService
from atlas.services.google_map_place_search_service import GoogleMapPlaceSearchService

RESULT_LIMIT = 20


class OutletSearchService(BaseService):
    """
    Searches outlets already known to us, then optionally tops up the results
    with Google Places matches that aren't in our database yet.

    Every result carries a `place_id` (the canonical identifier for an outlet,
    whether it lives in our database or only on Google) and an `is_added` flag
    telling the caller whether it already exists in our database.

    Calling:

        result, error = OutletSearchService.call(
            query="Truffles Bangalore",
            include_google_searches=True,
        )

        if not error:
            outlets = result["outlets"]
    """

    def perform(self):
        query = self.context["query"]
        include_google_searches = self.context.get("include_google_searches", True)

        outlets = []
        seen_place_ids = set()

        for outlet in self._search_local_outlets(query):
            seen_place_ids.add(outlet.place_id)
            outlets.append(self._serialize_local_outlet(outlet))

        if include_google_searches:
            google_result, error = GoogleMapPlaceSearchService.call(query=query)
            if not error:
                for place in google_result["places"]:
                    if place["place_id"] in seen_place_ids:
                        continue
                    seen_place_ids.add(place["place_id"])
                    outlets.append(self._serialize_google_place(place))

        self.result["outlets"] = outlets

    @staticmethod
    def _search_local_outlets(query):
        return Outlet.objects.filter(
            Q(name__icontains=query)
            | Q(city__icontains=query)
            | Q(address__icontains=query)
        )[:RESULT_LIMIT]

    @staticmethod
    def _serialize_local_outlet(outlet):
        return {
            "place_id": outlet.place_id,
            "name": outlet.name,
            "address": outlet.address,
            "city": outlet.city,
            "is_added": True,
        }

    @staticmethod
    def _serialize_google_place(place):
        return {
            "place_id": place["place_id"],
            "name": place["name"],
            "address": place["address"],
            "city": place["city"],
            "is_added": False,
        }
