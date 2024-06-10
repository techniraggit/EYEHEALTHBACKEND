from django.core.management.base import BaseCommand
import subprocess

commands = [
    "collectstatic --noinput",
]
class Command(BaseCommand):
    help = "To initialize initial configuration"

    def handle(self, *args, **options):
        """code to be here"""
        try:
            for command in commands:
                subprocess.call(f"python manage.py {command}", shell=True)
            self.stdout.write(
                self.style.SUCCESS("Initialized successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
