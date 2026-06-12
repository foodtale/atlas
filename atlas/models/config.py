import logging

from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from atlas.models.base import BaseModel

logger = logging.getLogger(__name__)

CACHE_TTL = 300


class Config(BaseModel):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True, default="")
    description = models.TextField(null=True, blank=True)
    is_depreciated = models.BooleanField(default=False)

    class Meta:
        db_table = "configs"

    def __str__(self):
        return self.key

    @classmethod
    def get(cls, key, default=None):
        cache_key = f"config:{key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        obj = cls.objects.filter(key=key).first()
        value = obj.value if obj else default

        if obj and obj.is_depreciated:
            logger.warning("Config key '%s' is deprecated and should no longer be used.", key)

        if value is not None:
            cache.set(cache_key, value, timeout=CACHE_TTL)

        return value


@receiver(post_save, sender=Config)
def bust_config_cache(sender, instance, **kwargs):
    cache.delete(f"config:{instance.key}")
