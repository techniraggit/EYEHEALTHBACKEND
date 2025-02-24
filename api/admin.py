from django.contrib import admin
from api.models.accounts import *
from api.models.notifications import *
from api.models.subscription import *
from api.models.rewards import *
from api.models.eye_health import *
from api.models.prescription import *
from api.models.static_pages import *
from api.models.dashboard import *
from api.models.blog import *


# Register your models here.
# ACCOUNT
@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email", "phone_number"]
    search_fields = ["email", "phone_number"]
    list_filter = ["deleted"]
    list_display.append("deleted")

    def get_queryset(self, request):
        return UserModel.all_objects.all().order_by("-created_on")


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ["user", "points", "event_type"]


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
    search_fields = ["username"]


@admin.register(DeviceInfo)
class DeviceInfoAdmin(admin.ModelAdmin):
    list_display = ["user", "system_id", "device_type", "created_on", "updated_on"]
    search_fields = ["user__email", "user__phone_number"]


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
        "is_active",
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
@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "message", "created_on"]
    search_fields = ["title"]


@admin.register(UserPushNotification)
class UserPushNotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "notification", "is_read", "created_on", "updated_on"]


# REWARDS
@admin.register(GlobalPointsModel)
class GlobalPointsModelAdmin(admin.ModelAdmin):
    list_display = ["id", "value", "event_type", "created_on", "updated_on"]

@admin.register(Offers)
class OffersAdmin(admin.ModelAdmin):
    list_display = [
        "offer_id",
        "title",
        "expiry_date",
        "status",
        "required_points",
    ]


@admin.register(EyeTestReport)
class EyeTestReportAdmin(admin.ModelAdmin):
    list_display = ["id", "report_id", "user_profile", "health_score"]
    search_fields = ["user_profile__full_name", "report_id", "user_profile__user__phone_number"]


@admin.register(EyeFatigueReport)
class EyeFatigueReportAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "report_id",
        "is_fatigue_right",
        "is_mild_tiredness_right",
        "is_fatigue_left",
        "is_mild_tiredness_left",
        "health_score",
        "created_on",
    ]
    search_fields = [
        "user__email",
        "user__phone_number",
        "report_id",
    ]


@admin.register(UserTestProfile)
class UserTestProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "full_name",
        "customer_id",
        "age",
    ]


@admin.register(UserRedeemedOffers)
class UserRedeemedOffersAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "offer",
        "status",
        "redeemed_on",
    ]


@admin.register(UserPrescriptions)
class UserPrescriptionsAdmin(admin.ModelAdmin):
    list_display = ["prescription_id", "status", "user"]
    search_fields = ["prescription_id", "user__email", "user__phone_number"]

@admin.register(StaticPages)
class StaticPagesAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created_by", "updated_by"]

@admin.register(UserContacts)
class UserContactsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "name",
        "phone_number",
    ]
    search_fields = [
        "user__email",
        "user__phone_number",
        "name",
        "phone_number",
    ]

@admin.register(CarouselModel)
class CarouselModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "image", "created_on"]
    search_fields = ["name"]

@admin.register(BlogModel)
class BlogModelAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
    search_fields = ["title"]
    date_hierarchy = "created_on"