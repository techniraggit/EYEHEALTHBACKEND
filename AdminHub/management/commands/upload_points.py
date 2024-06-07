from api.models.rewards import GlobalPointsModel
from django.core.management.base import BaseCommand
from core.constants import EVENT_CHOICES


class Command(BaseCommand):
    help = "Upload initial points."

    def handle(self, *args, **options):
        """code to be here"""
        try:
            for i in [event[0] for event in EVENT_CHOICES]:
                GlobalPointsModel.objects.get_or_create(event_type=i)

            self.stdout.write(
                self.style.SUCCESS("Points uploaded successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
