from django import forms
from store.models.models import BusinessModel, Stores
import re

phone_regex = r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$"
pin_code_regex = r"^\d{4,8}$"


class BusinessModelForm(forms.ModelForm):
    class Meta:
        model = BusinessModel
        fields = "__all__"


class StoreForm(forms.ModelForm):
    class Meta:
        model = Stores
        fields = [
            "business",
            "name",
            "gst_number",
            "pan_number",
            "description",
            "phone",
            "email",
            # "opening_time",
            # "closing_time",
            "latitude",
            "longitude",
            "pin_code",
            "address",
            "locality",
            "landmark",
            "city",
            "state",
            "country",
            "is_active",
        ]

    def clean_latitude(self):
        latitude = self.cleaned_data.get("latitude")
        if latitude is None or not (-90 <= latitude <= 90):
            raise forms.ValidationError("Latitude must be between -90 and 90.")
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get("longitude")
        if longitude is None or not (-180 <= longitude <= 180):
            raise forms.ValidationError("Longitude must be between -180 and 180.")
        return longitude

    def clean_phone(self):
        phone_number = self.cleaned_data.get("phone")
        if re.match(phone_regex, phone_number):
            return phone_number
        raise forms.ValidationError("Invalid phone number")

    def clean_pin_code(self):
        pin_code = self.cleaned_data.get("pin_code")
        if re.match(pin_code_regex, pin_code):
            return pin_code
        raise forms.ValidationError("Invalid pin code")

    def clean_is_active(self):
        status = self.data.get("status")
        return status == "active"
