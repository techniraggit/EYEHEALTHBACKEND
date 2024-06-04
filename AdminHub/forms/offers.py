from api.models.rewards import Offers
from django import forms

class OffersForm(forms.ModelForm):
    class Meta:
        model = Offers
        fields = ["title", "image", "description", "expiry_date", "status", "required_points"]