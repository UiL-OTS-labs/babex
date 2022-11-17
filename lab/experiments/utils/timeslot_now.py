from django.utils.datetime_safe import datetime
from pytz import timezone


def now() -> datetime:
    """This function returns a datetime object, set to the last minute that is
    a multiple of 5. Intended for a default value for a timeslot's datetime
    field.
    """
    datetime_now = datetime.now(tz=timezone('Europe/Amsterdam'))

    # Makes sure the minutes is a multiple of 5, by rounding down to the nearest
    minute = datetime_now.minute - (datetime_now.minute % 5)

    # We set tzinfo to 0 because it causes inconvenient output
    return datetime_now.replace(minute=minute, second=0, microsecond=0,
                                tzinfo=None)
