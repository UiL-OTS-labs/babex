from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ..models import Criterion, DefaultCriteria
from ..widgets import LanguageWidget


class DefaultCriteriaForm(forms.ModelForm):
    class Meta:
        model = DefaultCriteria
        fields = [
            'language', 'multilingual', 'sex', 'dyslexia',
            'min_age_months', 'min_age_days', 'max_age_months', 'max_age_days'
        ]

        widgets = {
            'language':      LanguageWidget,
            'multilingual':  forms.RadioSelect,
            'sex':           forms.RadioSelect,
            'dyslexia':      forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        # This removes the colon from the labels. Without it Django is very
        # inconsistent in it's use, so we just remove it
        kwargs.setdefault('label_suffix', '')
        super(DefaultCriteriaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # check that max age is greater than min age
        min_age_months, max_age_months = cleaned_data.get('min_age_months'), cleaned_data.get('max_age_months')
        min_age_days, max_age_days = cleaned_data.get('min_age_days'), cleaned_data.get('max_age_days')
        if min_age_months is not None and max_age_months is not None:
            if max_age_months < min_age_months or (max_age_months == min_age_months and max_age_days < min_age_days):
                raise ValidationError('Maximal age not greater than minimal age')

        return cleaned_data


class CriterionForm(forms.ModelForm):
    class Meta:
        model = Criterion
        fields = ['name_form', 'name_natural', 'values']
        widgets = {
            'name_form':     forms.TextInput,
            'name_natural':  forms.TextInput,
            'values':        forms.TextInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.criterionanswer_set.count() != 0:
            self.fields['values'].disabled = True

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


class ExperimentCriterionForm(forms.Form):

    name_form = forms.CharField(
        label=_('criterion:attribute:name_form'),
    )

    name_natural = forms.CharField(
        label=_('criterion:attribute:name_natural'),
    )

    values = forms.CharField(
        label=_('criterion:attribute:values'),
    )

    correct_value = forms.CharField(
        label=_('experiment_criterion:attribute:correct_value'),
    )

    message_failed = forms.CharField(
        label=_('experiment_criterion:attribute:message_failed'),
        widget=forms.Textarea({'cols': 35}),
    )

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
