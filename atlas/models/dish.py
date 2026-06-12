from django.db import models
from django.conf import settings

from atlas.models.base import BaseModel


class Dish(BaseModel):
    outlet = models.ForeignKey(
        "atlas.Outlet", on_delete=models.CASCADE, related_name="dishes"
    )
    name = models.CharField(max_length=255)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    public_tales_count = models.IntegerField(default=0)

    class Meta:
        db_table = "dishes"
        constraints = [
            models.UniqueConstraint(
                fields=["outlet", "name"], name="uniq_name_per_outlet"
            )
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.name = self.name.strip().lower()
        return super().save(*args, **kwargs)
