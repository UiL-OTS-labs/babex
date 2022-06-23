from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from datamanagement.utils.common import get_thresholds_model
from django.template import Library, Node, TemplateSyntaxError

register = Library()


class ThresholdNode(Node):
    _years = _('datamanagement:global:years')
    _months = _('datamanagement:global:months')
    _weeks = _('datamanagement:global:weeks')
    _days = _('datamanagement:global:days')

    def __init__(self, threshold, asvar):
        self.threshold = getattr(get_thresholds_model(), str(threshold), None)
        self.asvar = asvar

    def render(self, context):
        if self.threshold is not None:
            unit, value = self._get_display_values()
            val = "{} {}".format(value, unit)
        else:
            val = mark_safe('<strong>Unknown threshold</strong>')

        if self.asvar:
            context[self.asvar] = val
            return ''
        else:
            return val

    def _get_display_values(self):
        modulo_years = self.threshold % 365
        # Display in years if the threshold is in full years
        # (A margin is provided of 15 days below and 15 days above)
        if self.threshold > 365 and (modulo_years < 15 or modulo_years > 350):
            return self._years, round(self.threshold / 365)
        # Or, display in months if we have at least 2 months
        elif self.threshold > 62:
            return self._months, round(self.threshold / 30.417)
        # Or, display in days if we have less than 3 weeks
        elif self.threshold < 21:
            return self._days, self.threshold
        # Display in weeks for all other cases (should be more than 3 weeks
        # and less than 2 months)
        else:
            return self._weeks, round(self.threshold / 7)


@register.tag('threshold')
def do_translate_format(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument" % bits[0])
    threshold = parser.compile_filter(bits[1])

    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]

    return ThresholdNode(threshold, asvar)
