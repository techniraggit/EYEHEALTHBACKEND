from uuid import uuid4
from .base import BaseModel
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


from datetime import date


class UserModel(AbstractUser, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField("Email address", unique=True)
    image = models.FileField(upload_to="profile_image", null=True, blank=True)
    dob = models.DateField(null=True)
    points = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    referral_code = models.CharField(max_length=50, unique=True, null=True)
    customer_id = models.CharField(max_length=250, blank=True)

    username = None
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    def increase_points(self, points: int):
        self.points = self.points + points
        self.save()

    def age(self):
        today = date.today()
        age = (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )
        return age


class UserAddress(BaseModel):
    address_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="addresses"
    )
    address = models.TextField()
    postal_code = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="India")
    is_default = models.BooleanField(default=False)

    def get_full_address(self):
        return f"{self.user.get_full_name()}, {self.address}, {self.city}, {self.state}, {self.country}, {self.postal_code}"

    def to_json(self):
        return {
            "full_name": self.user.get_full_name(),
            "line1": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "state": self.state,
            "country": self.country,
        }


class DeviceInfo(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="device_info"
    )
    token = models.TextField()
    device_type = models.CharField(max_length=50)


class OTPLog(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    is_verify = models.BooleanField(default=False)


class ReferTrack(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    referred_by = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="referred_by"
    )
