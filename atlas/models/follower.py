from django.conf import settings
from django.db import models

from atlas.models.base import BaseModel


class Follower(BaseModel):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )

    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )

    class Meta:
        db_table = "followers"
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="uniq_follower_following",
            ),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F("following")),
                name="chk_no_self_follow",
            ),
        ]
