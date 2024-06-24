from .base import BaseModel, SoftDeleteMixin, SoftDeleteManager
from django.db import models
from .accounts import UserModel
from uuid import uuid4
from django.utils import timezone


class SubscriptionPlan(BaseModel, SoftDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    plan_type_choice = (
        ("basic", "basic"),
        ("monthly", "monthly"),
        ("quarterly", "quarterly"),
        ("yearly", "yearly"),
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    plan_type = models.CharField(max_length=30, choices=plan_type_choice)
    is_active = models.BooleanField(default=True)
    duration = models.IntegerField(help_text="Duration in days")

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def to_json(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            plan_type=self.plan_type,
            is_active=self.is_active,
            duration=self.duration,
        )

from utilities.utils import time_localize
class UserSubscription(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    payment_status_choices = (
        ("pending", "pending"),
        ("failed", "failed"),
        ("success", "success"),
    )
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=30)
    paid_amount = models.FloatField()
    payment_status = models.CharField(
        max_length=50, choices=payment_status_choices, default="pending"
    )

    def to_json(self):
        return dict(
            id=self.id,
            user=self.user.to_json(),
            plan=self.plan.name,
            start_date=self.start_date,
            end_date=self.end_date,
            is_active=self.is_active,
            payment_method=self.payment_method,
            paid_amount=self.paid_amount,
            payment_status=self.payment_status,
        )