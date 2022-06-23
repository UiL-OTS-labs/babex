from django.core.exceptions import ImproperlyConfigured
from django.forms import NumberInput


class TimespanWidget(NumberInput):
    """
    This widget is a variation of a number input intended to provide a
    human-friendly way to enter time spans. It will output the timespan in days.

    In the interface it will display the timespan in days, weeks, months or
    years. Users can select the mode with a select box, which the interface will
    convert on the fly. The default display mode can be supplied in the
    constructor, 'years' will be used if omitted.

    NOTE: For this widget to work you also need to load
    widgets/js/timespan_widget.js yourself! IT WILL NOT WORK WITHOUT IT.
    """
    template_name = 'widgets/timespan_widget.html'

    def __init__(self, default_display_mode='years', attrs=None):
        """
        :param default_display_mode: Either 'days', 'weeks', 'months' or 'years'
        :param attrs:
        """
        super().__init__(attrs)

        if default_display_mode not in ['days', 'weeks', 'months', 'years']:
            raise ImproperlyConfigured(
                "TimespanWidget needs default_display_mode to be one of 'days',"
                " 'weeks', 'months' or 'years'. It is: {}".format(
                    default_display_mode
                )
            )

        self.default_selection = default_display_mode

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['default_selection'] = self.default_selection
        return context
