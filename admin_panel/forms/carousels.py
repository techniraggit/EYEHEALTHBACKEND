from api.models.dashboard import CarouselModel
from django import forms

class CarouselModelForm(forms.ModelForm):
    class Meta:
        model = CarouselModel
        fields = "__all__"

    def clean_is_active(self):
        return self.data.get("status") == "active"