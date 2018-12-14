from django import forms

from ..models import Location


class CreateLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'
        widgets = {
            'name': forms.TextInput,
        }
