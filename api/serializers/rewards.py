from .base import BaseSerializer, serializers
from api.models.rewards import Offers, UserRedeemedOffers
from api.serializers.accounts import ProfileSerializer, UserAddressSerializer


class OffersSerializer(BaseSerializer):
    expiry = serializers.SerializerMethodField()

    class Meta:
        model = Offers
        fields = "__all__"

    def get_expiry(self, obj):
        return obj.get_expiry_time()

class UserRedeemedOffersSerializer(BaseSerializer):
    offer = OffersSerializer(fields=["offer_id", "title", "image", "description"])
    class Meta:
        model =  UserRedeemedOffers
        fields = "__all__"