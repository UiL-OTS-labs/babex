from typing import Union, Tuple
from json import JSONEncoder

from auditlog import settings

from auditlog.enums import Event, UserType
from auditlog.models import LogEntry
from main.models import User


def log(
        event: Event,
        message: str,
        user: Union[User, str] = None,
        user_type: UserType = None,
        extra: dict = None,
) -> None:
    """
    Adds an event to the audit log.

    :param event:
    :param message:
    :param user:
    :param user_type:
    :param extra: Any extra data that you want to log, in dict form. NOTE:
    Please only use datatypes that can be encoded by json.JSONEncoder. If
    you've got special datatypes, please encode them into a string manually!
    """
    # Stop directly if the log isn't enabled
    if not settings.AUDIT_LOG_ENABLE:
        return

    # Check if we need to actually log this event
    if not settings.AUDIT_LOG_LOGGABLE_EVENTS == '__all__' and \
            event not in settings.AUDIT_LOG_LOGGABLE_EVENTS:
        return

    user = _get_formatted_user(user)

    # Encode the extra data as JSON
    extra = _encode_extra_data(extra)

    event, user_type = _get_name_from_enums(event, user_type)

    # Do the actual logging
    LogEntry.objects.create(
        event=event,
        message=message,
        user=user,
        user_type=user_type,
        extra=extra
    )


def _get_name_from_enums(event: Event, user_type: UserType) -> Tuple[str, str]:
    if event is not None:
        event = event.name

    if user_type is not None:
        user_type = user_type.name

    return event, user_type


def _encode_extra_data(extra: dict) -> str:
    try:
        extra = JSONEncoder().encode(extra)
    except TypeError:
        # If it fails, provide some info about what is happening
        extra = {
            'error':    'unserializable data provided, original data is lost',
            'type':     str(type(extra)),
            '__str__':  str(extra),
            '__repr__': repr(extra),
        }
        extra = JSONEncoder().encode(extra)

    return extra


def _get_formatted_user(user: Union[User, str]) -> str:
    """
    This function tries to get a loggable string from the value in the
    `user` parameter. It will be formatted as '<type: info>

    It will do so by calling __audit_repr_(0) on any objects it detects,
    If this fails or the user parameter is either None or and empty string,
    it will return <Unknown user: [info]>. Where [info] will contain some
    basic info about why it's unknown.

    If it's already a string, the same string will be checked for format,
    and returned (in the correct format).

    :param user: An object to retrieve information from. Can be a User,
    ApiUser, a preformatted string or None.
    :return: The formatted representation
    """
    # Get the string representation for any user
    try:
        if user is not None and not isinstance(user, str):
            user = user.__audit_repr__()
    except AttributeError:
        user = "<Unknown user: couldn't call __audit_repr__ on supplied object>"

    if not user:
        user = "<Unknown user: no user info was supplied>"

    if not user.startswith('<'):
        user = "<{}".format(user)

    if not user.endswith('>'):
        user = "{}>".format(user)

    return user
