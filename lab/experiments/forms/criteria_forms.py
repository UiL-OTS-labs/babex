from cdh.core.forms import BootstrapRadioSelect, TemplatedModelForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ..models import DefaultCriteria
from ..widgets import LanguageWidget


class DefaultCriteriaForm(TemplatedModelForm):
    class Meta:
        model = DefaultCriteria
        fields = [
            "multilingual",
            "sex",
            "dyslexia",
            "min_age_months",
            "min_age_days",
            "max_age_months",
            "max_age_days",
        ]

        widgets = {
            "language": LanguageWidget,
            "multilingual": BootstrapRadioSelect,
            "sex": BootstrapRadioSelect,
            "dyslexia": BootstrapRadioSelect,
        }

    def __init__(self, *args, **kwargs):
        # This removes the colon from the labels. Without it Django is very
        # inconsistent in it's use, so we just remove it
        kwargs.setdefault("label_suffix", "")
        super(DefaultCriteriaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # check that max age is greater than min age
        min_age_months, max_age_months = cleaned_data.get("min_age_months"), cleaned_data.get("max_age_months")
        min_age_days, max_age_days = cleaned_data.get("min_age_days"), cleaned_data.get("max_age_days")
        if min_age_months is not None and max_age_months is not None:
            if max_age_months < min_age_months or (max_age_months == min_age_months and max_age_days < min_age_days):
                raise ValidationError("Maximal age not greater than minimal age")

        return cleaned_data
