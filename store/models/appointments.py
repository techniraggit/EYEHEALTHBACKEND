from django.conf import settings
from .models import BaseModel, models, Stores
from enum import Enum


class TimeSlot(BaseModel):
    start_time = models.TimeField(editable=False)

    class Meta:
        verbose_name_plural = "Time Slots"
        verbose_name = "Time Slot"

    def __str__(self):
        return f"{self.start_time}"


class Days(BaseModel):
    day = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name_plural = "Days"
        verbose_name = "Day"
        ordering = ["id"]

    def __str__(self):
        return f"{self.day}"


class HolidayType(Enum):
    PUBLIC = "Public"
    NATIONAL = "National"
    BANK = "Bank"
    RESTRICTED = "Restricted"
    GAZETTED = "Gazetted"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Holiday(BaseModel):
    name = models.CharField(max_length=50)
    type = models.CharField(choices=HolidayType.choices(), max_length=50, null=True)
    date = models.DateField()

    class Meta:
        verbose_name_plural = "Holidays"
        verbose_name = "Holiday"

    def __str__(self):
        return f"{self.name} {self.date.strftime('%Y-%m-%d')}"


class StoreHoliday(BaseModel):
    store = models.ForeignKey(Stores, on_delete=models.CASCADE)
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            "store",
            "holiday",
        )
        verbose_name_plural = "Store Holidays"
        verbose_name = "Store Holiday"

    def __str__(self):
        return f"{self.store} - {self.holiday.name}"


class StoreAvailability(BaseModel):
    store = models.ForeignKey(
        Stores, on_delete=models.CASCADE, related_name="store_availability"
    )
    start_working_hr = models.TimeField()
    end_working_hr = models.TimeField()
    days = models.ManyToManyField(Days)

    class Meta:
        verbose_name_plural = "Store Availabilities"
        verbose_name = "Store Availability"

    def __str__(self) -> str:
        return self.store.name

    @staticmethod
    def days_to_list(self):
        return [day.name for day in self.days.objects.all()]


class AppointmentSlot(BaseModel):
    store = models.ForeignKey(
        Stores,
        on_delete=models.CASCADE,
        related_name="store_appointment_slots",
        db_index=True,
    )
    date = models.DateField(db_index=True)
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name="time_appointments",
        db_index=True,
    )
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("store", "date", "time_slot")
        verbose_name_plural = "Appointment Slots"
        verbose_name = "Appointment Slot"
        indexes = [
            models.Index(fields=["store", "date", "time_slot"]),
        ]

    def __str__(self):
        return f"{self.store.name} - {self.date} - {self.time_slot}"


class AppointmentStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    choices = (
        ("PENDING", PENDING),
        ("CONFIRMED", CONFIRMED),
        ("CANCELLED", CANCELLED),
    )


class StoreAppointment(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_appointments",
        db_index=True,
    )
    # appointment = models.ForeignKey(
    #     AppointmentSlot, on_delete=models.SET_NULL, null=True, related_name="booked_appointment"
    # )
    status = models.CharField(
        max_length=50,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
    )
    service = models.CharField(max_length=50, blank=True, default="")
    notes = models.TextField(blank=True, null=True)
    store = models.ForeignKey(
        Stores,
        on_delete=models.CASCADE,
        related_name="store_booked_appointments",
        db_index=True,
    )
    date = models.DateField(db_index=True)
    time = models.TimeField()

    def __str__(self):
        return f"{self.user} - {self.store.name}"

    class Meta:
        verbose_name_plural = "Store Appointments"
        verbose_name = "Store Appointment"
        # unique_together = ("user", "appointment")
