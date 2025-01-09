from django.contrib import admin
from .models import (
    Services,
    Stores,
    StoreImages,
    Holiday,
    StoreHoliday,
    Days,
    Timing,
    StoreAvailability,
    StoreAppointment,
    BusinessModel,
    StoreRating,
)
from api.models.accounts import UserModel


# Register your models here.
@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_paid"]
    search_fields = ["name"]
    list_filter = ["is_paid"]
    # filter_horizontal = ["service"]


@admin.register(BusinessModel)
class BusinessModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email"]
    search_fields = ["name", "email"]


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


# admin.site.register(Services)
admin.site.register(StoreRating)
admin.site.register(StoreImages)
admin.site.register(Holiday)
admin.site.register(StoreHoliday)
admin.site.register(Days)
admin.site.register(Timing)
admin.site.register(StoreAvailability)
admin.site.register(StoreAppointment)
