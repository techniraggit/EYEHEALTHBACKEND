import os
import importlib.util
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Seeds the database with data from each app's seed.py file."

    def handle(self, *args, **kwargs):
        for app_config in apps.get_app_configs():
            seed_file_path = os.path.join(app_config.path, "seed.py")

            if os.path.exists(seed_file_path):
                self.stdout.write(
                    self.style.SUCCESS(f"Seeding data from '{app_config.name}")
                )
                self.run_seed_file(seed_file_path)

    def run_seed_file(self, seed_file_path):
        """Executes the seed.py file."""
        spec = importlib.util.spec_from_file_location("seed", seed_file_path)
        seed_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(seed_module)

        if hasattr(seed_module, "process"):
            seed_module.process()
        else:
            self.stdout.write(
                self.style.ERROR(f"No 'process' function found in '{seed_file_path}'.")
            )
