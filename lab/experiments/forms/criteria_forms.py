from cdh.core.forms import BootstrapCheckboxSelectMultiple, TemplatedModelForm
from django import forms
from django.core.exceptions import ValidationError

from ..models import DefaultCriteria


class DefaultCriteriaForm(TemplatedModelForm):
    show_valid_fields = False

    class Meta:
        model = DefaultCriteria
        fields = [
            "sex",
            "birth_weight",
            "pregnancy_duration",
            "multilingual",
            "dyslexic_parent",
            "tos_parent",
            "min_age_months",
            "min_age_days",
            "max_age_months",
            "max_age_days",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["sex", "birth_weight", "pregnancy_duration", "multilingual", "dyslexic_parent", "tos_parent"]:
            self.fields[field] = forms.MultipleChoiceField(
                label=self.instance._meta.get_field(field).verbose_name,
                choices=self.instance._meta.get_field(field).options,
                widget=BootstrapCheckboxSelectMultiple,
            )

    def clean(self):
        cleaned_data = super().clean()

        # check that max age is greater than min age
        min_age_months, max_age_months = cleaned_data.get("min_age_months"), cleaned_data.get("max_age_months")
        min_age_days, max_age_days = cleaned_data.get("min_age_days"), cleaned_data.get("max_age_days")
        if min_age_months is not None and max_age_months is not None:
            if max_age_months < min_age_months or (max_age_months == min_age_months and max_age_days < min_age_days):
                raise ValidationError("Maximal age not greater than minimal age")

        return cleaned_data
