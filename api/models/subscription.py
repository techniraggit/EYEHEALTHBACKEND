from .base import BaseModel
from django.db import models
from .accounts import UserModel
from uuid import uuid4


class SubscriptionPlan(BaseModel):
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
    plan_type = models.CharField(
        max_length=30, choices=plan_type_choice)
    is_active = models.BooleanField(default=True)


class UserSubscription(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    payment_status_choices = (
        ("pending", "pending"),
        ("failed", "failed"),
        ("success", "success"),
    )
    subscription_id = models.CharField(max_length=300)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=30)
    paid_amount = models.FloatField()
    payment_status = models.CharField(max_length=50, choices=payment_status_choices, default="pending")