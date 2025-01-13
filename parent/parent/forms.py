from datetime import date, timedelta

from ageutil import age
from cdh.core.forms import (
    BootstrapCheckboxInput,
    BootstrapCheckboxSelectMultiple,
    BootstrapRadioSelect,
    TemplatedForm,
    TemplatedFormTextField,
)
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class LanguagesWidget(forms.widgets.SelectMultiple):
    template_name = "widgets/languages_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value is None:
            return context

        if value == ["Nederlands"]:
            context["mono_dutch_checked"] = True
        elif len(value) == 1:
            context["mono_other_checked"] = True
            context["value"] = value
        elif len(value) > 1:
            context["multi_checked"] = True
            context["value"] = value
        return context

    def value_from_datadict(self, data, files, name):
        value = [v for v in data.getlist(name) if v]
        return value


class LanguagesField(forms.MultipleChoiceField):
    def to_python(self, value):
        v = super().to_python(value)
        if isinstance(v, str):
            v = [v]

        return list(filter(lambda x: x is not None and len(x), v))  # remove empty values

    def valid_value(self, value):
        return isinstance(value, str) and len(value) > 1

    def validate(self, value):
        super().validate(value)

        if len(value) < 1:
            # no languages
            raise ValidationError(_("parent:forms:languages:error:missing"))


class BirthDateWidget(forms.SelectDateWidget):
    template_name = "django/forms/widgets/birth_date.html"

    def __init__(self, min_date, max_date):
        super().__init__()
        self.min_date = min_date
        self.max_date = max_date

    def get_context(self, name, value, attrs):
        return dict(
            months={k: str(v) for k, v in self.months.items()},
            min_date=self.min_date,
            max_date=self.max_date,
            name=name,
            value=value,
        )

    def value_from_datadict(self, data, files, name):
        if all((data.get(name + "_year"), data.get(name + "_month"), data.get(name + "_day"))):
            # it seems logical to return here a date() object directly, however, Django doesn't
            # handle exceptions thrown here. if we return a string instead, it will be parsed in DateField.to_python()
            # which does  handle exceptions.
            return "{}-{}-{}".format(int(data[name + "_year"]), int(data[name + "_month"]), int(data[name + "_day"]))


class BirthDateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        min_date, max_date = age(0).to(years=2, months=6).range()
        self.widget = BirthDateWidget(min_date=min_date, max_date=max_date)
        self.validators = [MaxValueValidator(max_date), MinValueValidator(min_date)]


class SignupForm(TemplatedForm):
    baby_header = TemplatedFormTextField(header=_("parent:forms:signup:baby_header"))

    name = forms.CharField(label=_("parent:forms:signup:name"))
    sex = forms.ChoiceField(
        label=_("parent:forms:signup:sex"),
        required=True,
        choices=(
            ("F", _("parent:forms:signup:sex:f")),
            ("M", _("parent:forms:signup:sex:m")),
            ("UNK", _("parent:forms:signup:sex:unk")),
        ),
        widget=BootstrapRadioSelect(),
    )

    # birth_date: BirthDateField(  # re-initialized later because it uses current date in constructor

    birth_weight = forms.ChoiceField(
        label=_("parent:forms:signup:birth_weight"),
        choices=(
            ("LESS_THAN_2500", _("parent:forms:birth_weight:less_than_2500")),
            ("2500_TO_4500", _("parent:forms:birth_weight:2500_to_4500")),
            ("MORE_THAN_4500", _("parent:forms:birth_weight:more_than_4500")),
        ),
        widget=BootstrapRadioSelect(),
    )
    pregnancy_duration = forms.ChoiceField(
        label=_("parent:forms:signup:pregnancy_duration"),
        choices=(
            ("LESS_THAN_37", _("parent:forms:pregnancy_duration:less_than_37")),
            ("37_TO_42", _("parent:forms:pregnancy_duration:37_to_42")),
            ("MORE_THAN_42", _("parent:forms:pregnancy_duration:more_than_42")),
        ),
        widget=BootstrapRadioSelect(),
    )
    languages = LanguagesField(
        required=True,
        label=_("parent:forms:signup:languages"),
        widget=LanguagesWidget,
        choices=[],
    )
    parent_header = TemplatedFormTextField(header=_("parent:forms:signup:parent_header"))
    parent_first_name = forms.CharField(label=_("parent:forms:signup:parent_first_name"))
    parent_last_name = forms.CharField(label=_("parent:forms:signup:parent_last_name"))

    phonenumber = forms.CharField(
        label=_("parent:forms:signup:phonenumber"), widget=forms.TextInput(attrs={"type": "tel"})
    )
    phonenumber_alt = forms.CharField(
        label=_("parent:forms:signup:phonenumber_alt"), widget=forms.TextInput(attrs={"type": "tel"}), required=False
    )
    email = forms.CharField(
        label=_("parent:forms:signup:email"),
        help_text=_("parent:forms:signup:email:help_text"),
        widget=forms.TextInput(attrs={"type": "email"}),
    )
    email_again = forms.CharField(
        label=_("parent:forms:signup:email_again"), widget=forms.TextInput(attrs={"type": "email"})
    )

    dyslexic_parent = forms.ChoiceField(
        label=_("parent:forms:signup:dyslexic_parent"),
        required=True,
        choices=(
            ("F", _("parent:forms:signup:dyslexic_parent:f")),
            ("M", _("parent:forms:signup:dyslexic_parent:m")),
            ("BOTH", _("parent:forms:signup:dyslexic_parent:both")),
            ("NO", _("parent:forms:signup:dyslexic_parent:no")),
            ("UNK", _("parent:forms:signup:dyslexic_parent:unk")),
        ),
        widget=BootstrapRadioSelect(),
        help_text=_("parent:forms:signup:dyslexic_parent:help_text"),
    )

    tos_parent = forms.ChoiceField(
        label=_("parent:forms:signup:tos_parent"),
        required=True,
        choices=(
            ("F", _("parent:forms:signup:tos_parent:f")),
            ("M", _("parent:forms:signup:tos_parent:m")),
            ("BOTH", _("parent:forms:signup:tos_parent:both")),
            ("NO", _("parent:forms:signup:tos_parent:no")),
            ("UNK", _("parent:forms:signup:tos_parent:unk")),
        ),
        widget=BootstrapRadioSelect(),
        help_text=_("parent:forms:signup:tos_parent:help_text"),
    )

    general_header = TemplatedFormTextField(header=_("parent:forms:signup:general_header"))
    save_longer = forms.NullBooleanField(
        label=_("parent:forms:signup:save_longer"),
        help_text=_("parent:forms:signup:save_longer:help"),
        required=True,
        widget=BootstrapRadioSelect(choices=((True, _("Yes")), (False, _("No")))),
    )
    english_contact = forms.NullBooleanField(
        label=_("parent:forms:signup:english_contact"),
        help_text=_("parent:forms:signup:english_contact:help"),
        required=True,
        widget=BootstrapRadioSelect(choices=((True, _("Yes")), (False, _("No")))),
    )
    newsletter = forms.NullBooleanField(
        label=mark_safe(_("parent:forms:signup:newsletter")),
        help_text=_("parent:forms:signup:newsletter_help"),
        required=True,
        widget=BootstrapRadioSelect(choices=((True, _("Yes")), (False, _("No")))),
    )

    consent_header = TemplatedFormTextField(header=_("parent:forms:signup:consent_header"))
    # not saved anywhere, but it's a nice way to get a mandatory consent checkbox
    data_consent = forms.BooleanField(
        label="", widget=BootstrapCheckboxSelectMultiple(choices=((True, _("parent:forms:signup:data_consent")),))
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["birth_date"] = BirthDateField(
            label=_("parent:forms:signup:birth_date"),
            help_text=_("parent:forms:signup:birth_date:help_text"),
        )

        self.order_fields(['baby_header', 'name', 'sex', 'birth_date'])

        # replace the default django checkbox fields with bootstrap compatible ones
        for key, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget = BootstrapCheckboxInput()

    def clean(self):
        if self.cleaned_data["email"] != self.cleaned_data["email_again"]:
            self.add_error("email_again", forms.ValidationError(_("parent:forms:signup:email_again:error:email")))
