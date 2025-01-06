from enum import Enum
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import RegexValidator
from . import BaseModel, models


validator_contact = RegexValidator(
    regex=r"^[2-9][0-9]{9}$", message="Only Numbers allowed and cannot start with 0-5"
)


class Services(BaseModel):
    """
    Eye Test, Repair, Purchase
    """

    service = models.CharField(max_length=100)
    is_paid = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            "service",
            "is_paid",
        )
        db_table = "store_services"


class Stores(BaseModel):
    """
    images = {'image1': '', 'image2': ''}
    location = Point(28.42925912580746, 77.01704543758342)
    std.services.add(service)
    """

    name = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20, null=True, blank=True)
    pan_number = models.CharField(max_length=50, null=True, blank=True)
    services = models.ManyToManyField(Services)
    description = models.TextField()
    phone = models.CharField(max_length=10, validators=[validator_contact])
    location = PointField(geography=True, default=Point(0.0, 0.0))
    images = JSONField(default=dict)
    google_place_id = models.CharField(
        verbose_name="Google Place Id", max_length=256, null=True, blank=True
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pin_code = models.CharField(max_length=10)
    address = models.TextField()
    locality = models.CharField(max_length=128)
    landmark = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "store_details"

    def __str__(self):
        return self.google_place_id

    def __str__(self):
        return f"{self.id} - {self.name}"

    def full_address(self):
        return f"{self.address}, {self.locality}, {self.landmark}, {self.city}, {self.state} {self.pin_code}"


class StoreImages(BaseModel):
    store = models.ForeignKey(Stores, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="store_images")


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
        db_table = "holidays"


class StoreHoliday(BaseModel):
    store = models.ForeignKey(Stores, on_delete=models.CASCADE)
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE)

    class Meta:
        db_table = "store_holidays"
        unique_together = (
            "store",
            "holiday",
        )


class Days(models.Model):
    day = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = "days"


class Timing(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = (
            "start_time",
            "end_time",
        )
        db_table = "timings"


class StoreAvail(models.Model):
    store = models.ForeignKey(Stores, on_delete=models.CASCADE)
    day = models.ForeignKey(Days, on_delete=models.DO_NOTHING, null=True)
    timing = models.ForeignKey(Timing, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        db_table = "store_availability"
        unique_together = ("store", "day", "timing")


class StoreAppointment(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    name = models.CharField(max_length=255)
    store = models.ForeignKey(Stores, on_delete=models.CASCADE, db_index=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_slot = models.DateField(db_index=True)
    start_slot_time = models.TimeField()
    end_slot_time = models.TimeField()
    status = models.BooleanField(default=True)
    service = models.CharField(max_length=15, default="")

    def __str__(self):
        return self.name
