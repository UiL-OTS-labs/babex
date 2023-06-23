from datetime import date
from django import forms
from django.utils.translation import gettext_lazy as _

from cdh.core.forms import TemplatedForm
from cdh.core.forms import BootstrapCheckboxInput, BootstrapRadioSelect, DateField


def get_valid_year_range():
    """generates a list of valid birth years for the singup form"""
    end = date.today().year
    start = end - 10  # arbitrary limit on 10 years old, should probably be lower...
    return range(end, start, -1)


class ParticipantSexWidget(forms.widgets.Widget):
    template_name = 'widgets/participant_sex_widget.html'

    def value_from_datadict(self, data, files, name):
        value = data.get(name)

        if value == 'None':
            return None

        if value == "OTHER":
            value = data.get(name + '_other')

        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if context['widget']['value'] not in ['M', 'F']:
            context['widget']['other_value'] = context['widget']['value']
            context['widget']['value'] = 'OTHER'

        return context


class SignupForm(TemplatedForm):
    name = forms.CharField(label=_('parent:forms:signup:name'))
    sex = forms.ChoiceField(label=_('parent:forms:signup:sex'),
                            choices=(('F', _('parent:forms:signup:sex:f')),
                                     ('M', _('parent:forms:signup:sex:m'))),
                            widget=ParticipantSexWidget())
    birth_date = DateField(label=_('parent:forms:signup:birth_date'),
                           widget=forms.SelectDateWidget(years=get_valid_year_range()))

    parent_name = forms.CharField(label=_('parent:forms:signup:parent_name'))

    birth_weight = forms.IntegerField(label=_('parent:forms:signup:birth_weight'))
    pregnancy_weeks = forms.IntegerField(label=_('parent:forms:signup:pregnancy_weeks'))
    pregnancy_days = forms.IntegerField(label=_('parent:forms:signup:pregnancy_days'))

    phonenumber = forms.CharField(label=_('parent:forms:signup:phonenumber'))
    phonenumber_alt = forms.CharField(label=_('parent:forms:signup:phonenumber_alt'), required=False)
    email = forms.CharField(label=_('parent:forms:signup:email'))

    english_contact = forms.BooleanField(label=_('parent:forms:signup:english_contact'), required=False)
    newsletter = forms.BooleanField(label=_('parent:forms:signup:newsletter'), required=False)

    dyslexic_parent = forms.BooleanField(label=_('parent:forms:signup:dyslexic_parent'), required=False)
    multilingual = forms.BooleanField(label=_('parent:forms:signup:multilingual'), required=False)

    # not saved anywhere, but it's a nice way to get a mandatory consent checkbox
    data_consent = forms.BooleanField(label=_('parent:forms:signup:data_consent'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # replace the default django checkbox fields with bootstrap compatible ones
        for key, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget = BootstrapCheckboxInput()
