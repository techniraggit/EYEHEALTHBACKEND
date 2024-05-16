from .base import BaseModel
from django.db import models
from api.models.accounts import UserModel
from uuid import uuid4

class Offers(BaseModel):
    offer_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=250)
    image = models.FileField(upload_to="offer/images", null=True, blank=False)
    description = models.TextField()
    required_points = models.PositiveIntegerField()
    created_by = models.ForeignKey(UserModel, null=True, on_delete=models.SET_NULL, related_name="offers_created")
    updated_by = models.ForeignKey(UserModel, null=True, on_delete=models.SET_NULL)


class UserRedeemedOffers(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="redeemed_offers")
    offer = models.ForeignKey(Offers, on_delete=models.CASCADE)