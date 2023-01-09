
from main.models import User
from experiments.models import Location


def _get_or_create_leader() -> User:
    if User.objects.exists():
        return User.objects.first()  # type: ignore
    user = User.objects.create()
    return user


def _get_or_create_location() -> Location:
    if Location.objects.exists():
        return Location.objects.first()  # type: ignore
    return Location.objects.create(name="Cyberspace")
