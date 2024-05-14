from django.contrib import admin
from api.models.accounts import UserModel, OTPLog, DeviceInfo, ReferTrack


# Register your models here.
@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email", "phone_number"]
    search_fields = ["email", "phone_number"]


@admin.register(OTPLog)
class OTPLog(admin.ModelAdmin):
    list_display = ["username", "is_verify"]


@admin.register(DeviceInfo)
class DeviceInfoAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "device_type", "created_on", "updated_on"]


@admin.register(ReferTrack)
class ReferTrackAdmin(admin.ModelAdmin):
    list_display = ["user", "referred_by", "created_on", "updated_on"]
