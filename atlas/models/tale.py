from django.db import models
from django.conf import settings

from atlas.models.base import BaseModel
from atlas.models.choices import TaleVisibility


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
        choices=TaleVisibility.choices,
        default=TaleVisibility.PUBLIC,
    )
    photo = models.ForeignKey(
        "atlas.Attachment",
        on_delete=models.SET_NULL,
        related_name="attached_tale_photos",
        null=True,
        blank=True,
    )
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "tales"

    @property
    def photo_url(self):
        return self.photo.url

    @property
    def is_published(self):
        return self.published_at is not None


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
