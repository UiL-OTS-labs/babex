from main.models import User
from leaders.models import Leader
from .models import Location


def _get_or_create_leader() -> Leader:
    if Leader.objects.exists():
        return Leader.objects.first()  # type: ignore
    user = User.objects.create()
    return Leader.objects.create(user=user)


def _get_or_create_location() -> Location:
    if Location.objects.exists():
        return Location.objects.first()  # type: ignore
    return Location.objects.create(name="Cyberspace")
