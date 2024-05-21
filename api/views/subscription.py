from .base import UserMixin, APIView
from api.serializers.subscription import SubscriptionPlan, SubscriptionPlanSerializer
from core.utils import api_response


class SubscriptionPlansView(APIView):
    def get(self, request):
        subscriptions = SubscriptionPlan.objects.exclude(plan_type="basic").filter(is_active=True)
        subscriptions_data = SubscriptionPlanSerializer(subscriptions, many=True).data
        return api_response(True, 200, data=subscriptions_data)
