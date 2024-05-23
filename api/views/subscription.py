from .base import UserMixin, APIView
from api.serializers.subscription import (
    SubscriptionPlan,
    SubscriptionPlanSerializer,
    UserSubscription,
)
from core.utils import api_response


class IsActivePlan(UserMixin):
    def get(self, obj):
        plan_obj = UserSubscription.objects.filter(user=obj.user).order_by("created_on")
        is_active_plan = plan_obj.first().is_active if plan_obj.first() else False
        return api_response(True, 200, is_active_plan=is_active_plan)


class SubscriptionPlansView(APIView):
    def get(self, request):
        subscriptions = SubscriptionPlan.objects.exclude(plan_type="basic").filter(
            is_active=True
        )
        subscriptions_data = SubscriptionPlanSerializer(subscriptions, many=True).data
        return api_response(True, 200, data=subscriptions_data)
