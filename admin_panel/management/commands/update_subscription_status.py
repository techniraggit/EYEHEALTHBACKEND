from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models.subscription import UserSubscription


class Command(BaseCommand):
    help = "Updates the is_active field for expired subscriptions. 0 0 * * *"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        expired_subscriptions = UserSubscription.objects.filter(
            end_date__lt=today, is_active=True
        )

        for subscription in expired_subscriptions:
            subscription.is_active = False
            subscription.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully updated subscription statuses")
        )
