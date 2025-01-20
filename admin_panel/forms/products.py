from django import forms
from store.models.products import Frame


class FrameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].required = True
        self.fields['frame_type'].required = True

    class Meta:
        model = Frame
        fields = ['name', 'frame_type', 'gender', 'brand', 'image', 'is_recommended']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'frame_type': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
