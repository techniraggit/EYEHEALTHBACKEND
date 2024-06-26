from utilities.utils import generate_password
from utilities.services.email import send_email
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
        phone_number = "+"+self.cleaned_data.get("phone_number")
        if not is_valid_phone(phone_number):
            raise ValidationError("Not a valid phone number")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not is_valid_email(email):
            raise ValidationError("Not a valid email address")
        return email

    def clean_dob(self):
        dob = self.cleaned_data.get("dob")
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
            raise ValidationError(
                "If latitude is provided, longitude must also be provided."
            )

        return cleaned_data


class AdminCreationForm(forms.ModelForm):
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
        phone_number = "+" + self.cleaned_data.get("phone_number")
        if not is_valid_phone(phone_number):
            raise ValidationError("Not a valid phone number")

        if UserModel.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Phone number already exists.")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not is_valid_email(email):
            raise ValidationError("Not a valid email address")

        if UserModel.objects.filter(email=email).exists():
            raise ValidationError("Email address already exists.")
        return email

    def clean_dob(self):
        dob = self.cleaned_data.get("dob")
        today = datetime.now().date()
        if dob >= today:
            raise ValidationError("Date of birth cannot be in the future.")
        if dob < today - timedelta(days=365 * 150):
            raise ValidationError("Date of birth cannot be more than 150 years ago.")
        return dob

    def save(self, commit=True):
        user = super().save(commit=False)
        generated_password = generate_password()
        user.set_password(generated_password)
        user.is_admin = True
        email_subject = "Your Account has been Created"
        email_message = f"Hi {user.first_name} {user.last_name},\n\nYour account has been created.\n\nUsername: {user.email}\nPassword: {generated_password}"
        email_recipients = [user.email]

        if commit:
            user.save()
            send_email(
                subject=email_subject,
                message=email_message,
                recipients=email_recipients,
            )
        return user
