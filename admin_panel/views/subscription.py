from .base import AdminLoginView
from django.shortcuts import render
from api.models.subscription import SubscriptionPlan, UserSubscription
from django.http import JsonResponse



class SubscriptionView(AdminLoginView):
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        context = dict(
            plans = plans,
            is_subscription = True,
        )
        return render(request, "subscription/subscription.html", context)

class SubscriptionPlanDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Subscription Plan does not exist"}
            )
        return JsonResponse(
            {
                "status": True,
                "plan": plan_obj.to_json(),
            }
        )

from admin_panel.forms.subscription import SubscriptionPlanForm
import json
class SubscriptionEditView(AdminLoginView):
    def get(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Plan does not exist"}
            )
        context = dict(
            plan_obj = plan_obj,
            is_subscription = True,
        )
        return render(request, "subscription/edit_subscription.html", context)

    def post(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Plan does not exist"}
            )
        plan_form = SubscriptionPlanForm(request.POST, request.FILES, instance=plan_obj)
        if plan_form.is_valid():
            plan_obj = plan_form.save(commit=False)
            # plan_obj.updated_by = request.user
            plan_obj.save()
            return JsonResponse({"status": True, "message": "Plan updated successfully"})
        errors = plan_form.errors.as_json()
        parsed_data = json.loads(errors)
        first_key = next(iter(parsed_data))
        first_object = parsed_data[first_key][0]
        message = (
            f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
        )
        return JsonResponse({
            "status": False,
            "message": message,
        })


class SubscriptionAddView(AdminLoginView):
    def get(self, request):
        context = dict(
            is_subscription = True,
        )
        return render(request, "subscription/add_subscription.html", context)
    
    def post(self, request):
        plan_form = SubscriptionPlanForm(request.POST)
        if plan_form.is_valid():
            plan_form.save()
            return JsonResponse({"status": True, "message": "Plan added successfully"})
        errors = plan_form.errors.as_json()
        parsed_data = json.loads(errors)
        first_key = next(iter(parsed_data))
        first_object = parsed_data[first_key][0]
        message = (
            f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
        )
        return JsonResponse({
            "status": False,
            "message": message,
        })

class SubscriptionDeleteView(AdminLoginView):
    def get(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Plan does not exist"}
            )
        plan_obj.delete()
        return JsonResponse({"status": True, "message": "Plan deleted successfully"})
class UserSubscriptionView(AdminLoginView):
    def get(self, request):
        user_plans = UserSubscription.objects.all()
        context = dict(
            user_plans = user_plans,
            is_user_subscription = True,
        )
        return render(request, "subscription/user_subscription.html", context)