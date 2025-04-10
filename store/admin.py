from django.contrib import admin
from .models.models import (
    Services,
    Stores,
    StoreImages,
    BusinessModel,
    StoreRating,
)
from .models.appointments import (
    Holiday,
    StoreHoliday,
    Days,
    StoreAvailability,
    StoreAppointment,
    TimeSlot,
    AppointmentSlot,
)
from .models.products import (
    Frame,
    FrameTypes,
    Brands,
)


# Register your models here.
@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_paid"]
    search_fields = ["name"]
    list_filter = ["is_paid"]
    # filter_horizontal = ["service"]


@admin.register(BusinessModel)
class BusinessModelAdmin(admin.ModelAdmin):
    list_display = ["user", "name"]
    search_fields = ["name", "user__email", "user__phone_number"]


@admin.register(Stores)
class StoresAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    filter_horizontal = ["services"]
    search_fields = ["name"]

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "company":
    #         # Filter to show only companies (users with `is_company=True`)
    #         kwargs["queryset"] = UserModel.objects.filter(is_company=True)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(StoreAvailability)
class StoreAvailabilityAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "start_working_hr", "end_working_hr"]
    search_fields = ["store__name"]
    list_filter = ["days"]
    filter_horizontal = ["days"]


@admin.register(StoreAppointment)
class StoreAppointmentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "store", "date", "time", "status"]
    search_fields = ["user__email", "store__name"]
    date_hierarchy = "date"
    list_filter = ["store"]


@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    list_display = ["name", "frame_type", "gender", "brand", "is_recommended"]
    search_fields = ["name"]


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ["store", "date", "time_slot", "is_booked"]
    list_filter = ["store", "is_booked"]
    date_hierarchy = "date"


admin.site.register(StoreRating)
admin.site.register(StoreImages)
admin.site.register(Holiday)
admin.site.register(StoreHoliday)
admin.site.register(Days)
admin.site.register(TimeSlot)
admin.site.register(FrameTypes)
admin.site.register(Brands)
