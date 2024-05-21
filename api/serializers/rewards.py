from .base import BaseSerializer, serializers
from api.models.rewards import Offers


class OffersSerializer(BaseSerializer):
    expiry = serializers.SerializerMethodField()

    class Meta:
        model = Offers
        fields = "__all__"

    def get_expiry(self, obj):
        return obj.get_expiry_time()
