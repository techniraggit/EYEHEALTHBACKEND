from utilities.utils import time_localize
from django.utils import timezone
from django.http import JsonResponse
import json
from .base import AdminLoginView
from django.shortcuts import render, redirect
from api.models.rewards import Offers
from api.models.subscription import SubscriptionPlan
from django.contrib import messages
from api.models.accounts import UserModel
from django.db import IntegrityError


class TrashView(AdminLoginView):
    def get(self, request):
        trash_users = UserModel.all_objects.filter(deleted__isnull=False).order_by("-deleted")
        trash_offers = Offers.all_objects.filter(deleted__isnull=False).order_by("-deleted")
        trash_plans = SubscriptionPlan.all_objects.filter(deleted__isnull=False).order_by("-deleted")
        context = dict(
            trash_users = trash_users,
            trash_offers = trash_offers,
            trash_plans = trash_plans,
            is_trash=True,
        )
        return render(request, "trash/trash.html", context)

class RestoreUserView(AdminLoginView):
    def get(self, request, id):
        try:
            user = UserModel.all_objects.get(pk=id)
        except UserModel.DoesNotExist:
            return JsonResponse({
                "status": False,
                "message": "User does not exist",
            })
        try:
            user.phone_number = str(user.phone_number).split("/")[0]
            user.email = str(user.email).split("/")[0]
            user.deleted = None
            user.save()
            return JsonResponse({
                "status": True,
                "message": "User restored successfully",
            })
        except IntegrityError:
            return JsonResponse({
                "status": False,
                "message": "User cannot be restored",
            })
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e),
            })


class RestoreOfferView(AdminLoginView):
    def get(self, request, id):
        try:
            offer_obj = Offers.all_objects.get(pk=id)
        except Offers.DoesNotExist:
            return JsonResponse({
                "status": False,
                "message": "Offer does not exist",
            })
        try:
            offer_obj.deleted = None
            offer_obj.save()
            return JsonResponse({
                "status": True,
                "message": "Offer restored successfully",
            })
        except IntegrityError:
            return JsonResponse({
                "status": False,
                "message": "Offer cannot be restored",
            })
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e),
            })

class RestoreSubscriptionPlanView(AdminLoginView):
    def get(self, request, id):
        try:
            plan_obj = SubscriptionPlan.all_objects.get(pk=id)
        except SubscriptionPlan.DoesNotExist:
            return JsonResponse({
                "status": False,
                "message": "Subscription Plan does not exist",
            })
        try:
            plan_obj.deleted = None
            plan_obj.save()
            return JsonResponse({
                "status": True,
                "message": "Subscription Plan restored successfully",
            })
        except IntegrityError:
            return JsonResponse({
                "status": False,
                "message": "Plan cannot be restored",
            })
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e),
            })