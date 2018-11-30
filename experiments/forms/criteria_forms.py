from django import forms

from ..models import DefaultCriteria
from ..widgets import LanguageWidget


class DefaultCriteriaForm(forms.ModelForm):
    class Meta:
        model = DefaultCriteria
        fields = '__all__'
        widgets = {
            'experiment': forms.HiddenInput,
            'language': LanguageWidget,
            'multilingual': forms.RadioSelect,
            'sex': forms.RadioSelect,
            'handedness': forms.RadioSelect,
            'dyslexia': forms.RadioSelect,
            'social_status': forms.RadioSelect,
        }
