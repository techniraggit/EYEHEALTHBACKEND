from api.models.dashboard import CarouselModel
from django import forms

class CarouselModelForm(forms.ModelForm):
    class Meta:
        model = CarouselModel
        fields = "__all__"