from django.db import models
from django.conf import settings

from atlas.models.base import BaseModel
from atlas.models.choices import FoodTaleVisibility


class Tale(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tales"
    )
    outlet = models.ForeignKey(
        "atlas.Outlet", on_delete=models.CASCADE, related_name="tales"
    )
    dish = models.ForeignKey(
        "atlas.Dish", on_delete=models.CASCADE, related_name="tales"
    )
    would_order_again = models.BooleanField(default=True)
    story = models.TextField(blank=True, null=True)
    liked_tales_count = models.IntegerField(default=0)
    visibility = models.CharField(
        max_length=32,
        choices=FoodTaleVisibility.choices,
        default=FoodTaleVisibility.FOLLOWERS,
    )

    class Meta:
        db_table = "tales"


class TalePhoto(BaseModel):
    tale = models.ForeignKey(
        "atlas.Tale", on_delete=models.CASCADE, related_name="photos"
    )
    photo = models.ForeignKey(
        "atlas.Attachment",
        on_delete=models.CASCADE,
        related_name="attached_tale_photos",
    )

    class Meta:
        db_table = "tale_photos"

    @property
    def photo_url(self):
        return self.photo.url


class TaleLike(BaseModel):
    tale = models.ForeignKey(
        "atlas.Tale", on_delete=models.CASCADE, related_name="likes"
    )
    liked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_tales",
    )

    class Meta:
        db_table = "tale_likes"
        constraints = [
            models.UniqueConstraint(
                fields=["tale", "liked_by"],
                name="uniq_tale_like_per_user",
            )
        ]
