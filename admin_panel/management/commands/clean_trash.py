from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models.subscription import SubscriptionPlan
from api.models.rewards import Offers
from core.logs import Logger

logger = Logger("trash.log")

class Command(BaseCommand):
    help = "Empty Trash"

    def handle(self, *args, **kwargs):
        current_date = (timezone.now() - timezone.timedelta(days=90)).date()

        models = [SubscriptionPlan, Offers] # List of Models 
        for model in models:
            self.clean_trash(model, current_date)

        self.stdout.write(self.style.SUCCESS("Successfully cleaned trash"))

    def clean_trash(self, model, current_date):
        try:
            deleted_count, _ = model.all_objects.filter(deleted__date=current_date).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} {model.__name__}(s)"))
        except Exception as e:
            logger.error(f"Could not find {model.__name__.lower()}: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Could not find {model.__name__.lower()}: {str(e)}"))

