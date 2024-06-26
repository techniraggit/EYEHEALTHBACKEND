from django.contrib import admin
from .models import Credentials

# Register your models here.
admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ["name",  "created_on", "updated_on"]
    search_fields = ["name"]