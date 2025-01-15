from django.db.models import Avg
from django.conf import settings
from django.contrib.gis.measure import D  # For distances
from django.contrib.gis.db.models.functions import Distance
from uuid import uuid4
from enum import Enum
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models import PointField
from django.core.validators import RegexValidator
from api.models.accounts import BaseModel, models


validator_contact = RegexValidator(
    regex=r"^\+[1-9][0-9]{1,3}[0-9]{7,10}$",
    message="The contact number must start with a '+' followed by a country code (1-3 digits) and a phone number (7-10 digits)."
)


class StoresManager(models.Manager):
    def nearby_stores(self, user_location, radius_km=15):
        return (
            self.get_queryset()
            .filter(
                is_active=True, location__distance_lte=(user_location, D(km=radius_km))
            )
            .annotate(distance=Distance("location", user_location))
            .order_by("distance")  # Closest stores first
        )

    def all_stores(self, user_location):
        return (
            self.get_queryset()
            .annotate(distance=Distance("location", user_location))
            .order_by("distance")  # Closest stores first
        )


class Services(BaseModel):
    """
    Eye Test, Repair, Purchase
    """

    name = models.CharField(max_length=100)
    is_paid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = (
            "name",
            "is_paid",
        )
        verbose_name_plural = "Services"
        verbose_name = "Service"


class BusinessModel(BaseModel):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, validators=[validator_contact], unique=True)
    email = models.EmailField(unique=True)
    logo = models.FileField(upload_to="business_logo", null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def to_json(self):
        return dict(
            id=self.id,
            name=self.name,
            phone=self.phone,
            email=self.email,
            last_login=self.last_login.strftime("%Y-%m-%d %H:%M %p") if self.last_login else None,
            status="Active" if self.is_active else "Inactive",
        )


class Stores(BaseModel):
    """
    images = {'image1': '', 'image2': ''}
    location = Point(28.42925912580746, 77.01704543758342)
    std.services.add(service)
    """

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    business = models.ForeignKey(
        BusinessModel, on_delete=models.CASCADE, related_name="stores"
    )
    name = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20, null=True, blank=True)
    pan_number = models.CharField(max_length=50, null=True, blank=True)
    services = models.ManyToManyField(Services, related_name="stores")
    description = models.TextField()
    phone = models.CharField(max_length=10, validators=[validator_contact])
    email = models.EmailField()
    location = PointField(geography=True, default=Point(0.0, 0.0))
    images_as_json = models.JSONField(default=dict, null=True)
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

    objects = models.Manager()
    store_manage = StoresManager()

    class Meta:
        # db_table = "store_details"
        verbose_name_plural = "Stores"
        verbose_name = "Store"

    def __str__(self):
        return self.name

    def full_address(self):
        return f"{self.address}, {self.locality}, {self.landmark}, {self.city}, {self.state} {self.pin_code}"

    def get_average_rating(self):
        """
        Calculate and return the average rating of the store.
        """
        average_rating = self.ratings.aggregate(average=Avg("rating"))["average"]
        return round(average_rating, 2) if average_rating else 0.0

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(self.longitude, self.latitude)
            super().save(*args, **kwargs)

    def to_json(self):
        store_timing  = self.store_availability.all().first()
        return {
            "id": self.id,
            "name": self.name,
            "gst_number": self.gst_number,
            "pan_number": self.pan_number,
            "services": list(self.services.all().values_list("name", flat=True)),
            "description": self.description,
            "phone": self.phone,
            "email": self.email,
            "opening_time": store_timing.start_working_hr.strftime("%I:%M %p"),
            "closing_time": store_timing.end_working_hr.strftime("%I:%M %p"),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "pin_code": self.pin_code,
            "address": self.full_address(),
            "is_active": "Active" if self.is_active else "Inactive",
        }


class StoreImages(BaseModel):
    store = models.ForeignKey(Stores, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="store_images")


class StoreRating(BaseModel):
    store = models.ForeignKey(Stores, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_ratings"
    )
    rating = models.PositiveIntegerField()
    review = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("store", "user")
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.store.name} - {self.rating} by {self.user.email}"
