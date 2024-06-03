from .base import AdminLoginView
from django.shortcuts import render
from api.models.subscription import SubscriptionPlan, UserSubscription



class SubscriptionView(AdminLoginView):
    records_per_page = 10
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        context = dict(
            plans = plans,
            is_subscription = True,
        )
        return render(request, "subscription/subscription.html", context)