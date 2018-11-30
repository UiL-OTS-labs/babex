from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from ..models import DefaultCriteria, Criterium
from ..widgets import LanguageWidget


class DefaultCriteriaForm(forms.ModelForm):
    class Meta:
        model = DefaultCriteria
        fields = '__all__'
        widgets = {
            'experiment':    forms.HiddenInput,
            'language':      LanguageWidget,
            'multilingual':  forms.RadioSelect,
            'sex':           forms.RadioSelect,
            'handedness':    forms.RadioSelect,
            'dyslexia':      forms.RadioSelect,
            'social_status': forms.RadioSelect,
        }


class CriteriumForm(forms.ModelForm):
    class Meta:
        model = Criterium
        fields = ['name_form', 'name_natural', 'values', 'correct_value',
                  'message_failed']
        widgets = {
            'name_form':     forms.TextInput,
            'name_natural':  forms.TextInput,
            'values':        forms.TextInput,
            'correct_value': forms.TextInput,
        }

    def clean_name_form(self):
        """Slugifies the form name"""
        return slugify(self.cleaned_data['name_form'])

    def clean_values(self):
        """
        Removes any whitespace in the values
        """
        values = self.cleaned_data['values'].split(',')
        cleaned = []

        for value in values:
            cleaned.append(value.strip())

        return ','.join(cleaned)

    def clean_correct_value(self):
        """Makes sure correct_value is actually one of the values that can be
        chosen.
        """
        values = self.cleaned_data['values'].strip().split(',')
        correct_value = self.cleaned_data['correct_value']

        if correct_value not in values:
            raise forms.ValidationError(_(
                'criteria:form:correct_value:error:not_a_value'))

        return correct_value
