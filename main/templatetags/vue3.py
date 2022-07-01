import datetime
import random
import string
import json

from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()


class VueJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()


@register.simple_tag(takes_context=True)
def vue(context, component, *args, **kwargs):
    """
    Embeds a vue component in place, and accepts binding to props via kwargs
    """

    binding = mark_safe(
        '\n'.join('data["{}"] = {};'.format(k, json.dumps(v, cls=VueJSONEncoder)) for k, v in kwargs.items()))

    # add a random suffix to container id, to avoid collisions
    suffix = ''.join(random.sample(string.ascii_lowercase, 5))
    container = '_'.join(component.split('.') + [suffix])

    return format_html('''
    <div id="{container}"></div>
    <script>
    (function() {{
    let data = {{}};
    {binding}
        createApp({component}, data).mount('#{container}')
    }})();
    </script>''',
                       binding=binding,
                       component=component,
                       container=container)
