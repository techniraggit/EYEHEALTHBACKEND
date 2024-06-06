import logging
from django.utils import timezone
from utilities.services.email import send_email
from django.http import JsonResponse
import json
from django.urls import reverse
from .base import AdminLoginView
from django.shortcuts import render, redirect
from api.models.rewards import Offers, UserRedeemedOffers
from AdminHub.forms.offers import OffersForm, GlobalPointsModel
from django.contrib import messages

logger = logging.getLogger(__name__)


class SettingsView(AdminLoginView):
    def get(self, request):
        points = GlobalPointsModel.objects.all().order_by("-created_on")
        context = dict(
            points=points,
            is_settings=True,
        )
        return render(request, "settings/settings.html", context)

    def post(self, request):
        id = request.POST.get("id")
        points = request.POST.get("points")

        if not all([id, points]):
            return JsonResponse(
                {"status": False, "message": "Required fields are missing"}
            )

        try:
            points_obj = GlobalPointsModel.objects.get(pk=id)
        except GlobalPointsModel.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Points object does not exist"}
            )

        try:
            points = int(points)
        except ValueError:
            return JsonResponse(
                {"status": False, "message": "Invalid value for points"}
            )

        points_obj.value = points
        points_obj.save()

        logger.info(f"Points updated for id {id}: {points}")

        event_name = points_obj.event.title().replace("_", " ")

        return JsonResponse(
            {"status": True, "message": f"{event_name} points updated successfully"}
        )
