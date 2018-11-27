from django import forms

from ..models import DefaultCriteria


class DefaultCriteriaForm(forms.ModelForm):
    class Meta:
        model = DefaultCriteria
        fields = '__all__'
        widgets = {
            'experiment': forms.HiddenInput,
            # TODO: special widget for language
            'language': forms.TextInput,
            'multilingual': forms.RadioSelect,
            'sex': forms.RadioSelect,
            'handedness': forms.RadioSelect,
            'dyslexia': forms.RadioSelect,
            'social_status': forms.RadioSelect,
        }
