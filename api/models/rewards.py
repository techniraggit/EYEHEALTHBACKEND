from core.constants import EVENT_CHOICES
from .base import BaseModel, SoftDeleteMixin, SoftDeleteManager, models
from django.db import models
from api.models.accounts import UserModel, UserAddress
from uuid import uuid4
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class Offers(BaseModel, SoftDeleteMixin):
    offer_status = (
        ("active", "active"),
        ("inactive", "inactive"),
        ("expired", "expired"),
    )
    offer_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=250)
    image = models.FileField(
        upload_to="offer/images",
        null=True,
        blank=False,
        validators=[
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "gif"])
        ],
    )
    description = models.TextField()
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=offer_status, default="active")
    required_points = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        UserModel, null=True, on_delete=models.SET_NULL, related_name="offers_created"
    )
    updated_by = models.ForeignKey(UserModel, null=True, on_delete=models.SET_NULL)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def get_expiry_time(self):
        current_time = timezone.now()
        expiry_time = self.expiry_date
        time_difference = expiry_time - current_time
        if time_difference.total_seconds() > 0:
            days = time_difference.days
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"Time remaining: {days} days, {hours:02}:{minutes:02}:{seconds:02}"
        else:
            self.status = "expired"
            self.save()
            return "offer expired"

    def update_offer_status(self):
        current_time = timezone.now()
        expiry_time = self.expiry_date
        time_difference = expiry_time - current_time
        if time_difference.total_seconds() > 0:
            if self.status == "expired":
                self.status = "active"
        else:
            self.status = "expired"
        self.save()


class UserRedeemedOffers(BaseModel):
    offer_status_choices = (
        ("pending", "pending"),
        ("dispatched", "dispatched"),
        ("emailed", "emailed"),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="redeemed_offers"
    )
    offer = models.ForeignKey(Offers, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50, choices=offer_status_choices, default="pending"
    )
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True)
    redeemed_on = models.DateTimeField(auto_now_add=True)
    emailed_on = models.DateTimeField(null=True, blank=True)
    email_body = models.TextField(null=True, blank=True)
    email_subject = models.CharField(max_length=250, null=True, blank=True)
    dispatch_address = models.TextField(blank=True, null=True)
    dispatch_on = models.DateTimeField(null=True, blank=True)


class GlobalPointsModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    value = models.IntegerField(default=0)
    event_type = models.CharField(
        max_length=50, choices=EVENT_CHOICES, unique=True, null=True
    )
