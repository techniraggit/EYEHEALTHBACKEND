from django.db.models import F
from store.models.appointments import (
    AppointmentSlot,
    StoreAppointment,
    AppointmentStatus,
)
from datetime import datetime
from core.utils import api_response
from django.db import transaction
from store.views.base import UserMixin


def is_valid_date(date, date_formate):
    try:
        datetime.strptime(date, date_formate)
        return True
    except:
        return False


class TimeSlotsView(UserMixin):
    def get(self, request):
        store_id = request.GET.get("store_id")
        date = request.GET.get("date")
        if not store_id or not date:
            return api_response(False, 400, message="Store ID and date are required.")

        if not is_valid_date(date, "%Y-%m-%d"):
            return api_response(
                False, 400, message="Invalid date format. Please use '%Y-%m-%d'."
            )

        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()

        today = datetime.today().date()
        if not parsed_date >= today:
            return api_response(False, 400, message="The provided date is not valid.")

        current_date_time = datetime.now()
        if parsed_date == current_date_time.date():
            avail = (
                AppointmentSlot.objects.filter(
                    store__id=store_id,
                    date=parsed_date,
                    is_booked=False,
                    time_slot__start_time__gt=current_date_time.time(),
                )
                .distinct()
                .order_by("time_slot__start_time")
                .annotate(slot_time=F("time_slot__start_time"))
                .values("slot_time", "id")
            )
        else:
            avail = (
                AppointmentSlot.objects.filter(
                    store__id=store_id, date=parsed_date, is_booked=False
                )
                .distinct()
                .order_by("time_slot__start_time")
                .annotate(slot_time=F("time_slot__start_time"))
                .values("slot_time", "id")
            )
        return api_response(True, 200, data=avail)


class BookAppointmentView(UserMixin):
    def post(self, request, slot_id):
        try:
            slot = AppointmentSlot.objects.get(id=slot_id)
        except:
            return api_response(False, 404, message="Slot not found.")

        if slot.is_booked:
            return api_response(False, 400, message="Slot is already booked.")

        try:
            with transaction.atomic():
                store_app_obj = StoreAppointment.objects.create(
                    user=request.user,
                    # appointment=slot,
                    store=slot.store,
                    date=slot.date,
                    time=slot.time_slot.start_time,
                    status=AppointmentStatus.CONFIRMED,
                    service="",
                    notes="",
                )
                slot.is_booked = True
                slot.save()
                appointment_details = dict(
                    UserName=request.user.first_name,
                    StoreName=slot.store.name,
                    Address=slot.store.full_address(),
                    Time=store_app_obj.time.strftime("%I:%M %p"),
                    Date=store_app_obj.date.strftime("%d-%m-%Y"),
                )
                return api_response(
                    True,
                    200,
                    message="Appointment booked successfully.",
                    data=appointment_details,
                )
        except Exception as e:
            return api_response(False, 500, message=str(e))


class BookedAppointmentsView(UserMixin):
    def get(self, request):
        appointments_qs = StoreAppointment.objects.filter(user=request.user).order_by(
            "date"
        )
        data = []
        for appointment in appointments_qs:
            data.append(
                {
                    "id": str(appointment.id),
                    "StoreName": appointment.store.name,
                    "address": appointment.store.full_address(),
                    "date": appointment.date.strftime("%d-%m-%Y"),
                    "time": appointment.time.strftime("%I:%M %p"),
                }
            )
        return api_response(True, 200, data=data)
