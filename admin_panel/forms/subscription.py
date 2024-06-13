from api.models.subscription import SubscriptionPlan
from django import forms

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
