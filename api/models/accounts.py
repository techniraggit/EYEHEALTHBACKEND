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


class UserModel(AbstractUser, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField("Email address", unique=True)
    image = models.FileField(upload_to="profile_image", null=True, blank=True)
    points = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    referral_code = models.CharField(max_length=50, unique=True, null=True)

    username = None
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]



class DeviceInfo(BaseModel):
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="device_info"
    )
    token = models.TextField()
    device_type = models.CharField(max_length=50)


class OTPLog(BaseModel):
    username = models.CharField(max_length=50, unique=True)
    is_verify = models.BooleanField(default=False)


class ReferTrack(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    referred_by = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="referred_by"
    )
