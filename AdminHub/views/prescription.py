from api.models.rewards import GlobalPointsModel
from core.logs import Logger
from api.models.accounts import UserPoints
from .base import AdminLoginView
from django.shortcuts import render, redirect, get_object_or_404
from api.models.prescription import UserPrescriptions
from django.contrib import messages
from django.urls import reverse

logger = Logger("prescription.logs")

class PrescriptionView(AdminLoginView):
    def get(self, request):
        prescriptions = UserPrescriptions.objects.all()
        context = dict(
            prescriptions=prescriptions,
            is_prescription=True,
        )
        return render(request, "prescription/prescription.html", context)


class PrescriptionDetailView(AdminLoginView):
    def get(self, request, id):
        prescription_obj = UserPrescriptions.objects.get(prescription_id=id)
        context = dict(
            prescription_obj=prescription_obj,
            is_prescription=True,
        )
        return render(request, "prescription/prescription_view.html", context)


class ChangePrescriptionStatusView(AdminLoginView):
    def get(self, request, id, status):
        if status not in ["approved", "rejected"]:
            messages.error(request, "Invalid status")
            return redirect(reverse("prescription_detailed_view", args=[id]))

        prescription_obj = get_object_or_404(UserPrescriptions, prescription_id=id)
        prescription_obj.status = status
        prescription_obj.save()
        if status == "approved":
            try:
                points = GlobalPointsModel.objects.get(
                    event_type="prescription_upload"
                ).value
                UserPoints.objects.create(
                    user=prescription_obj.user,
                    points=points,
                    event_type="prescription_upload",
                )
            except Exception as e:
                logger.error(str(e))

        messages.success(request, f"Prescription {status} successfully")
        return redirect(reverse("prescription_detailed_view", args=[id]))
