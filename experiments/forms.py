from django import forms

from .models import Experiment


class CreateExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = '__all__'
        widgets = {
            'name': forms.TextInput,
            'duration': forms.TextInput,
            'compensation': forms.TextInput,
        }
