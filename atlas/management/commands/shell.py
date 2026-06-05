from django.core.management.commands import shell
from atlas import services


class Command(shell.Command):
    def get_auto_imports(self):
        names = getattr(services, "__all__", [])
        return super().get_auto_imports() + [f"atlas.services.{n}" for n in names]