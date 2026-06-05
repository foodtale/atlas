import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from atlas.models.config import Config


class Command(BaseCommand):
    help = "Sync config metadata " "(description, is_depreciated) from configs.json"

    def handle(self, *args, **options):
        config_file = Path(settings.BASE_DIR) / "configs.json"

        with open(config_file) as f:
            configs = json.load(f)

        existing_configs = {config.key: config for config in Config.objects.all()}

        configs_to_update = []

        for config_data in configs:
            obj = existing_configs.get(config_data["key"])

            if not obj:
                self.stdout.write(
                    self.style.WARNING(
                        f"Config '{config_data['key']}' not found in DB. "
                        "Run seed_configs first."
                    )
                )
                continue

            changed = False

            description = config_data.get("description")
            is_depreciated = config_data.get("is_depreciated", False)

            if obj.description != description:
                obj.description = description
                changed = True

            if obj.is_depreciated != is_depreciated:
                obj.is_depreciated = is_depreciated
                changed = True

            if changed:
                configs_to_update.append(obj)

        if configs_to_update:
            Config.objects.bulk_update(
                configs_to_update,
                ["description", "is_depreciated"],
            )

        self.stdout.write(
            self.style.SUCCESS(f"Updated {len(configs_to_update)} config(s)")
        )
