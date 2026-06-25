import logging

from django.db import transaction
from django.db.models import F

from atlas.models.attachment import Attachment
from atlas.models.choices import TaleVisibility
from atlas.models.dish import Dish
from atlas.models.outlet import Outlet
from atlas.models.tale import Tale
from atlas.services.base import BaseService
from atlas.services.google_map_place_detail_service import GoogleMapPlaceDetailService

logger = logging.getLogger(__name__)


class CreateTaleService(BaseService):
    """
    Creates a tale end-to-end.

    Resolves outlet (DB-first, Google fallback) and dish, then inside a single
    transaction: creates the tale with optional photo, clears the attachment
    expiry to make it permanent, and increments all denormalised counters.

    Usage:
        result, error = CreateTaleService.call(
            user=request.user,
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
            dish_name="butter chicken",
            story="Amazing food!",
            would_order_again=True,
            visibility="public",
            attachment_id="uuid",   # optional
        )

        if not error:
            tale = result["tale"]
    """

    def perform(self):
        user = self.context["user"]
        place_id = self.context["place_id"]
        dish_name = self.context["dish_name"].strip().lower()
        story = self.context.get("story", "")
        would_order_again = self.context.get("would_order_again", True)
        visibility = self.context.get("visibility", TaleVisibility.PUBLIC)
        attachment_id = self.context.get("photo_id")
        is_public = visibility == TaleVisibility.PUBLIC

        place_data = self._fetch_place_if_needed(place_id)
        attachment = self._resolve_attachment(attachment_id, user)

        with transaction.atomic():
            outlet = self._resolve_outlet(place_id, place_data, user)
            dish = self._resolve_dish(outlet, dish_name, user)

            tale = Tale.objects.create(
                user=user,
                outlet=outlet,
                dish=dish,
                story=story,
                would_order_again=would_order_again,
                visibility=visibility,
                photo=attachment,
            )

            if attachment:
                attachment.expires_at = None
                attachment.save(update_fields=["expires_at"])

            self._increment_counters(user, dish, is_public)

        self.result["tale"] = tale

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _fetch_place_if_needed(self, place_id: str) -> dict | None:
        if Outlet.objects.filter(place_id=place_id).exists():
            return None

        result, error = GoogleMapPlaceDetailService.call(place_id=place_id)
        if error:
            self.fail(message=f"Could not resolve outlet: {error.message}")

        return result["place"]

    def _resolve_attachment(self, attachment_id: str | None, user) -> Attachment | None:
        if not attachment_id:
            return None

        attachment = Attachment.objects.filter(
            id=attachment_id,
            uploaded_by=user,
        ).first()

        if not attachment:
            self.fail(message="Photo attachment not found.")

        return attachment

    def _resolve_outlet(self, place_id: str, place_data: dict | None, user) -> Outlet:
        if place_data is None:
            return Outlet.objects.get(place_id=place_id)

        outlet, _ = Outlet.objects.get_or_create(
            place_id=place_id,
            defaults={
                "name": place_data["name"] or "",
                "address": place_data["address"] or "",
                "city": place_data["city"] or "",
                "state": place_data["state"] or "",
                "country": place_data["country"] or "",
                "postal_code": place_data["postal_code"] or "",
                "latitude": place_data["latitude"],
                "longitude": place_data["longitude"],
                "added_by": user,
            },
        )
        return outlet

    def _resolve_dish(self, outlet: Outlet, dish_name: str, user) -> Dish:
        dish, _ = Dish.objects.get_or_create(
            outlet=outlet,
            name=dish_name,
            defaults={"added_by": user},
        )
        return dish

    def _increment_counters(self, user, dish: Dish, is_public: bool) -> None:
        user_fields = {"tales_count": F("tales_count") + 1}
        if is_public:
            user_fields["public_tales_count"] = F("public_tales_count") + 1

        user.__class__.objects.filter(pk=user.pk).update(**user_fields)

        if is_public:
            Dish.objects.filter(pk=dish.pk).update(
                public_tales_count=F("public_tales_count") + 1
            )
