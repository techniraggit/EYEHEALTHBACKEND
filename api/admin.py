from django.contrib import admin
from api.models.accounts import *
from api.models.notifications import *
from api.models.subscription import *
from api.models.rewards import *
from api.models.eye_health import *


# Register your models here.
# ACCOUNT
@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email", "phone_number"]
    search_fields = ["email", "phone_number"]


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = [
        "address_id",
        "user",
        "address",
        "postal_code",
        "city",
        "state",
        "country",
    ]
    search_fields = ["user__email", "user__phone_number"]


@admin.register(OTPLog)
class OTPLog(admin.ModelAdmin):
    list_display = ["username", "is_verify"]


@admin.register(DeviceInfo)
class DeviceInfoAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "device_type", "created_on", "updated_on"]


@admin.register(ReferTrack)
class ReferTrackAdmin(admin.ModelAdmin):
    list_display = ["user", "referred_by", "created_on", "updated_on"]


# SUBSCRIPTION
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "price",
        "plan_type",
        "created_on",
        "updated_on",
    ]


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "plan",
        "start_date",
        "end_date",
        "is_active",
        "created_on",
        "updated_on",
    ]


# NOTIFICATION
admin.register(PushNotification)


@admin.register(UserPushNotification)
class UserPushNotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "notification", "is_read", "created_on", "updated_on"]


# REWARDS


@admin.register(Offers)
class OffersAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "image",
        "description",
        "required_points",
        "created_on",
        "updated_on",
    ]


@admin.register(UserRedeemedOffers)
class OffersAdmin(admin.ModelAdmin):
    list_display = ["user", "offer", "created_on", "updated_on"]

@admin.register(EyeTestReport)
class EyeTestReportAdmin(admin.ModelAdmin):
    list_display = ["user_eye_test"]

@admin.register(EyeFatigueReport)
class EyeFatigueReportAdmin(admin.ModelAdmin):
    list_display = ["user_eye_test"]