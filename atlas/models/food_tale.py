from django.db import models
from django.conf import settings

from atlas.models.base import BaseModel
from atlas.models.choices import FoodTaleVisibility


class FoodTale(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_tales"
    )
    outlet = models.ForeignKey(
        "atlas.Outlet", on_delete=models.CASCADE, related_name="food_tales"
    )
    dish = models.ForeignKey(
        "atlas.Dish", on_delete=models.CASCADE, related_name="food_tales"
    )
    would_order_again = models.BooleanField(default=True)
    story = models.TextField(blank=True, null=True)
    liked_food_tales_count = models.IntegerField(default=0)
    visibility = models.CharField(
        max_length=32,
        choices=FoodTaleVisibility.choices,
        default=FoodTaleVisibility.FOLLOWERS,
    )

    class Meta:
        db_table = "food_tales"


class FoodTalePhoto(BaseModel):
    food_tale = models.ForeignKey(
        "atlas.FoodTale", on_delete=models.CASCADE, related_name="photos"
    )
    photo = models.ForeignKey(
        "atlas.Attachment",
        on_delete=models.CASCADE,
        related_name="attached_food_tale_photos",
    )

    class Meta:
        db_table = "food_tale_photos"


class FoodTaleLike(BaseModel):
    food_tale = models.ForeignKey(
        "atlas.FoodTale", on_delete=models.CASCADE, related_name="likes"
    )
    liked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_food_tales",
    )

    class Meta:
        db_table = "food_tale_likes"
        constraints = [
            models.UniqueConstraint(
                fields=["food_tale", "liked_by"],
                name="uniq_food_tale_like_per_user",
            )
        ]
