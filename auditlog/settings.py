"""This module loads in the project's setting file and tries to get the
config this app uses from there. If a certain setting isn't in the settings
file, it will default to a predefined value."""
from django.conf import settings

_DEFAULTS = {
    'AUDIT_LOG_ENABLE': False,
    'AUDIT_LOG_LOGGABLE_EVENTS': '__all__'  # Either a list of events to log,
    # or the magic value '__all__'
}

AUDIT_LOG_ENABLE = getattr(
    settings,
    'AUDIT_LOG_ENABLE',
    _DEFAULTS['AUDIT_LOG_ENABLE']
)

AUDIT_LOG_LOGGABLE_EVENTS = getattr(
    settings,
    'AUDIT_LOG_LOGGABLE_EVENTS',
    _DEFAULTS['AUDIT_LOG_LOGGABLE_EVENTS']
)
