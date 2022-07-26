import datetime
import random
import string
import json
from functools import partial

from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()


class VueJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if hasattr(obj, '_wrapped'):
            return super().encode(obj._wrapped)
        return super().encode(obj)

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)


def prop_const(const, context):
    return json.dumps(const, cls=VueJSONEncoder)


def prop_variable(name, context):
    return json.dumps(context[name], cls=VueJSONEncoder)


def prop_code(code, context):
    return code


def event_prop(name):
    return 'on' + name[0].upper() + name[1:]


@register.tag
def vue(parser, token):
    args = token.split_contents()

    inline = False
    if 'inline' in args:
        args.remove('inline')
        inline = True

    component = args[1]
    props = dict()
    for i in range(len(args)):
        if args[i][0] == ':':
            # prop binding
            rest = args[i][1:]
            if '=' not in rest:
                # treat :thing the same as :thing=thing
                name = rest
                props[name] = partial(prop_variable, name)
            else:
                (name, value) = args[i][1:].split('=')
                if value[0] in ['"', "'"]:
                    props[name] = partial(prop_const, value[1:-1])
                else:
                    props[name] = partial(prop_variable, name)
        elif args[i][0] == '@':
            (name, value) = args[i][1:].split('=')
            props[event_prop(name)] = partial(prop_code, value[1:-1])

    return VueRenderer(component, props, inline)


class VueRenderer(template.Node):
    def __init__(self, component, props, inline):
        self.component = component
        self.props = props
        self.inline = inline

    def render(self, context):
        binding_defs = []
        for prop, value in self.props.items():
            binding_defs.append('data["{}"] = {};'.format(prop, value(context)))

        binding = mark_safe('\n'.join(binding_defs))

        # add a random suffix to container id, to avoid collisions
        suffix = ''.join(random.sample(string.ascii_lowercase, 5))
        container = '_'.join(self.component.split('.') + [suffix])

        style = 'display:inline' if self.inline else ''

        return format_html('''
        <div id="{container}" style="{style}"></div>
        <script>
        (function() {{
        let data = {{}};
        {binding}
            createApp({component}, data).mount('#{container}')
        }})();
        </script>''',
                           binding=binding,
                           component=self.component,
                           container=container,
                           style=style)
