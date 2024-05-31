from .base import AdminLoginView
from django.shortcuts import render
from api.models.prescription import UserPrescriptions



class PrescriptionView(AdminLoginView):
    records_per_page = 10
    def get(self, request):
        prescriptions = UserPrescriptions.objects.all()
        context = dict(
            prescriptions = prescriptions,
            is_prescription = True,
        )
        return render(request, "prescription/prescription.html", context)