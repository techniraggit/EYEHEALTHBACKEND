from django import forms
from django.core.exceptions import ValidationError
from api.models.accounts import UserModel
from datetime import datetime, timedelta
from utilities.utils import is_valid_phone, is_valid_email

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "dob",
            "image",
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not is_valid_phone(phone_number):
            raise ValidationError("Not a valid phone number")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not is_valid_email(email):
            raise ValidationError("Not a valid email address")
        return email

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        today = datetime.now().date()
        if dob >= today:
            raise ValidationError("Date of birth cannot be in the future.")
        if dob < today - timedelta(days=365 * 150):
            raise ValidationError("Date of birth cannot be more than 150 years ago.")
        return dob

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")
        dob = cleaned_data.get("dob")

        if not dob:
            raise ValidationError("DOB required.")

        if latitude is not None and longitude is None:
            raise ValidationError("If latitude is provided, longitude must also be provided.")

        return cleaned_data
