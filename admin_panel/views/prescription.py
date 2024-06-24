from utilities.services.email import send_email
from utilities.services.notification import create_notification
from django.http import JsonResponse
from api.models.rewards import GlobalPointsModel
from core.logs import Logger
from api.models.accounts import UserPoints
from .base import AdminLoginView
from django.shortcuts import render, get_object_or_404
from api.models.prescription import UserPrescriptions
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

logger = Logger("prescription.logs")


class PrescriptionView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        status_filter = request.GET.get("status_filter")
        prescription_qs = UserPrescriptions.objects.all().order_by("-created_on")

        if search:
            prescription_qs = prescription_qs.filter(
                Q(prescription_id__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(status=str(search).lower())
            )

        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            prescription_qs = prescription_qs.filter(created_on__gte=start_date_filter)

        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            prescription_qs = prescription_qs.filter(created_on__lte=end_date_filter)

        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            prescription_qs = prescription_qs.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )

        if status_filter:
            prescription_qs = prescription_qs.filter(status=status_filter)

        paginator = Paginator(prescription_qs, 10)
        page_number = request.GET.get("page")
        paginated_prescriptions = paginator.get_page(page_number)
        context = dict(
            prescriptions=paginated_prescriptions,
            is_prescription=True,
            search = search,
            start_date_filter = start_date_filter,
            end_date_filter = end_date_filter,
            status_filter = status_filter,
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

        subject = f"Your Prescription was {status.title()}"
        message = f"Your Prescription was {status.title()} uploaded on {prescription_obj.created_on.strftime('%Y-%m-%d')}"
        send_email(
            subject=subject, message=message, recipients=[prescription_obj.user.email]
        )
        create_notification(
            user_ids=[prescription_obj.user.id], title=subject, message=message
        )
        return JsonResponse(
            {"status": True, "message": f"Prescription {status} successfully"}
        )
