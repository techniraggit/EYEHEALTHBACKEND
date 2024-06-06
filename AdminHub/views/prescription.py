from django.http import JsonResponse
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
    def post(self, request, id):
        status = request.POST.get("status")
        rejection_notes = request.POST.get("rejection_notes", None)

        if status not in ["approved", "rejected"]:
            return JsonResponse({"status": False, "message": "Invalid status"})

        prescription_obj = get_object_or_404(UserPrescriptions, prescription_id=id)
        prescription_obj.status = status
        if status == "approved":
            try:
                points = GlobalPointsModel.objects.get(
                    event_type="prescription_upload"
                ).value
                usr_pnt = UserPoints.objects.create(
                    user=prescription_obj.user,
                    event_type="prescription_upload",
                )
                usr_pnt.increase_points(points)
                usr_pnt.save()
            except Exception as e:
                logger.error(str(e))
        else:
            prescription_obj.rejection_notes = rejection_notes
        prescription_obj.save()
        return JsonResponse(
            {"status": True, "message": f"Prescription {status} successfully"}
        )
