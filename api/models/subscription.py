from .base import BaseModel
from django.db import models
from .accounts import UserModel


class SubscriptionPlan(BaseModel):
    TYPE_CHOICE = (
        ("monthly", "monthly"),
        ("quarterly", "quarterly"),
        ("yearly", "yearly"),
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_type = models.CharField(
        max_length=30, choices=TYPE_CHOICE, null=True, blank=True
    )


class Subscription(BaseModel):
    STATUS_CHOICE = (
        ("active", "active"),
        ("inactive", "inactive"),
    )
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICE, default="inactive")


class Payment(BaseModel):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=30)
    trans_id = models.TextField()
    # Add other fields like payment method, transaction ID, etc.
