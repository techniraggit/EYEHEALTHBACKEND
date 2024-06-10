from api.models.rewards import Offers, GlobalPointsModel
from django import forms
from django.utils import timezone
from datetime import timedelta

class OffersForm(forms.ModelForm):
    class Meta:
        model = Offers
        fields = ["title", "image", "description", "expiry_date", "status", "required_points"]
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get("expiry_date")
        today = timezone.now()
        one_year_from_today = today + timedelta(days=365)

        if expiry_date <= today:
            raise forms.ValidationError("Expiry date must be greater than today.")

        if expiry_date > one_year_from_today:
            raise forms.ValidationError("Expiry date must be less than 1 year from today.")

        return expiry_date

class GlobalPointsForm(forms.ModelForm):
    model = GlobalPointsModel
    fields = ["value", "event"]