from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models.models import BusinessModel

UserModel = get_user_model()
class Command(BaseCommand):
    help = "Associate existing BusinessModel entries with UserModel"

    def handle(self, *args, **kwargs):
        businesses = BusinessModel.objects.filter(user__isnull=True)

        for business in businesses:
            user, created = UserModel.objects.get_or_create(
                email=business.email,
                defaults={
                    "phone_number": business.phone,
                    "password": business.password if business.password else "creator@123",
                },
            )
            business.user = user
            business.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully associated {businesses.count()} BusinessModel entries with UserModel"))

