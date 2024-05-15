from .base import BaseModel
from django.db import models
from api.models.accounts import UserModel

class Offers(BaseModel):
    title = models.CharField(max_length=250)
    image = models.FileField(upload_to="offer/images", null=True, blank=False)
    description = models.TextField()
    required_points = models.PositiveIntegerField()
    created_by = models.ForeignKey(UserModel, on_delete=models.DO_NOTHING, related_name="offers_created")
    updated_by = models.ForeignKey(UserModel, on_delete=models.DO_NOTHING)


class UserRedeemedOffers(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="redeemed_offers")
    offer = models.ForeignKey(Offers, on_delete=models.CASCADE)