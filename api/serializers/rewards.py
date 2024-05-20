from .base import BaseSerializer
from api.models.rewards import Offers


class OffersSerializer(BaseSerializer):
    class Meta:
        model = Offers
        fields = "__all__"
