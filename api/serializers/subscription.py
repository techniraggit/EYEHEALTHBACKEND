from api.models.subscription import *
from .base import BaseSerializer


class SubscriptionPlanSerializer(BaseSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
