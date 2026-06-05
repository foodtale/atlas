import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from atlas.models.config import Config


class Command(BaseCommand):
    help = "Create missing configs from configs.json"

    def handle(self, *args, **options):
        config_file = Path(settings.BASE_DIR) / "configs.json"

        with open(config_file) as f:
            configs = json.load(f)

        created = 0

        for config in configs:
            _, was_created = Config.objects.get_or_create(
                key=config["key"],
                defaults={
                    "value": config["value"],
                    "description": config.get("description"),
                    "is_depreciated": config.get("is_depreciated", False),
                },
            )

            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} config(s)"))
