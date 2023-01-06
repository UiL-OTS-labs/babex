from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _

from cdh.core.forms import TemplatedForm
from cdh.core.forms import BootstrapCheckboxInput, BootstrapRadioSelect, DateField


def get_valid_year_range():
    end = date.today().year
    start = end - 10
    return range(end, start, -1)


class SignupForm(TemplatedForm):
    name = forms.CharField(label=_('parent:forms:signup:name'))
    sex = forms.ChoiceField(label=_('parent:forms:signup:sex'),
                            choices=(('F', _('parent:forms:signup:sex:f')),
                                     ('M', _('parent:forms:signup:sex:m'))),
                            widget=BootstrapRadioSelect())
    birth_date = DateField(label=_('parent:forms:signup:birth_date'),
                           widget=forms.SelectDateWidget(years=get_valid_year_range()))

    parent_name = forms.CharField(label=_('parent:forms:signup:parent_name'))
    city = forms.CharField(label=_('parent:forms:signup:city'))
    phonenumber = forms.CharField(label=_('parent:forms:signup:phonenumber'))
    phonenumber_alt = forms.CharField(label=_('parent:forms:signup:phonenumber_alt'), required=False)
    email = forms.CharField(label=_('parent:forms:signup:email'))

    english_contact = forms.BooleanField(label=_('parent:forms:signup:english_contact'), required=False)
    newsletter = forms.BooleanField(label=_('parent:forms:signup:newsletter'), required=False)

    dyslexic_parent = forms.BooleanField(label=_('parent:forms:signup:dyslexic_parent'), required=False)
    tos_parent = forms.BooleanField(label=_('parent:forms:signup:tos_parent'), required=False)
    speech_parent = forms.BooleanField(label=_('parent:forms:signup:speech_parent'), required=False)
    multilingual = forms.BooleanField(label=_('parent:forms:signup:multilingual'), required=False)

    data_consent = forms.BooleanField(label=('parent:forms:signup:data_consent'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget = BootstrapCheckboxInput()
