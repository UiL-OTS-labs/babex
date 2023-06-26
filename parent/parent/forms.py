from datetime import date

from cdh.core.forms import (
    BootstrapCheckboxInput,
    BootstrapRadioSelect,
    DateField,
    TemplatedForm,
)
from django import forms
from django.utils.translation import gettext_lazy as _


def get_valid_year_range():
    """generates a list of valid birth years for the singup form"""
    end = date.today().year
    start = end - 10  # arbitrary limit on 10 years old, should probably be lower...
    return range(end, start, -1)


class ParticipantSexWidget(forms.widgets.Widget):
    template_name = "widgets/participant_sex_widget.html"

    def value_from_datadict(self, data, files, name):
        value = data.get(name)

        if value == "None":
            return None

        if value == "OTHER":
            value = data.get(name + "_other")

        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if context["widget"]["value"] not in ["M", "F"]:
            context["widget"]["other_value"] = context["widget"]["value"]
            context["widget"]["value"] = "OTHER"

        return context


class PregnancyDurationField(forms.MultiValueField):
    class Widget(forms.widgets.MultiWidget):
        template_name = "widgets/pregnancy_duration_widget.html"

        def __init__(self, *args, **kwargs):
            widgets = [forms.widgets.NumberInput, forms.widgets.NumberInput]
            super().__init__(widgets, *args, **kwargs)

        def decompress(self, value):
            if value is None:
                return (None, None)
            return value

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(label=_("parent:forms:signup:pregnancy_weeks")),
            forms.IntegerField(label=_("parent:forms:signup:pregnancy_days")),
        )
        super().__init__(fields, *args, widget=PregnancyDurationField.Widget(), **kwargs)

    def compress(self, values):
        return values


class SignupForm(TemplatedForm):
    name = forms.CharField(label=_("parent:forms:signup:name"))
    sex = forms.CharField(
        label=_("parent:forms:signup:sex"),
        widget=ParticipantSexWidget(),
    )
    birth_date = DateField(
        label=_("parent:forms:signup:birth_date"), widget=forms.SelectDateWidget(years=get_valid_year_range())
    )

    parent_name = forms.CharField(label=_("parent:forms:signup:parent_name"))

    birth_weight = forms.IntegerField(label=_("parent:forms:signup:birth_weight"))

    pregnancy_duration = PregnancyDurationField()

    phonenumber = forms.CharField(label=_("parent:forms:signup:phonenumber"))
    phonenumber_alt = forms.CharField(label=_("parent:forms:signup:phonenumber_alt"), required=False)
    email = forms.CharField(label=_("parent:forms:signup:email"))

    dyslexic_parent = forms.ChoiceField(
        label=_("parent:forms:signup:dyslexic_parent"),
        required=True,
        choices=(
            ("F", _("parent:forms:signup:dyslexic_parent:f")),
            ("M", _("parent:forms:signup:dyslexic_parent:m")),
            ("BOTH", _("parent:forms:signup:dyslexic_parent:both")),
            ("NO", _("parent:forms:signup:dyslexic_parent:no")),
        ),
        widget=BootstrapRadioSelect(),
    )

    multilingual = forms.BooleanField(
        label=_("parent:forms:signup:multilingual"),
        required=False,
        widget=BootstrapRadioSelect(choices=((True, _("Yes")), (False, _("No")))),
    )

    english_contact = forms.BooleanField(
        label=_("parent:forms:signup:english_contact"),
        required=False,
        widget=BootstrapRadioSelect(choices=((True, _("Yes")), (False, _("No")))),
    )
    newsletter = forms.BooleanField(
        label=_("parent:forms:signup:newsletter"),
        required=False,
        widget=BootstrapRadioSelect(choices=((True, _("Yes")), (False, _("No")))),
    )

    # not saved anywhere, but it's a nice way to get a mandatory consent checkbox
    data_consent = forms.BooleanField(label=_("parent:forms:signup:data_consent"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # replace the default django checkbox fields with bootstrap compatible ones
        for key, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget = BootstrapCheckboxInput()
