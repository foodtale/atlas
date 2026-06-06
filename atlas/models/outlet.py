from django.db import models
from django.conf import settings

from atlas.models.base import BaseModel


class Outlet(BaseModel):
    place_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    postal_code = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "outlets"
