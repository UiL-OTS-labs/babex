from django.conf import settings

from .models import Leader
from api.auth.models import ApiUser, ApiGroup


def create_leader(name: str, email: str, phonenumber: str,
                  password: str = None) -> Leader:
    """
    This function creates a new Leader object.

    If the email specified is already used, it will return the Leader object for
    that email.

    If there already is a ApiUser object with that email, that one will be
    retrieved and used in the Leader object. This can happen if someone who
    already made an account as a participant is added as a leader.

    If no ApiUser object exists, one will be created.

    In both cases the ApiUser object is added to the leader group.

    :param name:
    :param email:
    :param phonenumber:
    :param password:
    :return:
    """
    _leader_group = ApiGroup.objects.get(name=settings.LEADER_GROUP)
    existing_leader = Leader.objects.filter(api_user__email=email)

    if existing_leader:
        return existing_leader[0]

    leader = Leader()
    leader.name = name
    leader.phonenumber = phonenumber

    existing_api_user = ApiUser.objects.filter(email=email)

    if existing_api_user:
        api_user = existing_api_user[0]
    else:
        api_user = ApiUser()
        api_user.email = email

        if password:
            api_user.set_password(password)

        api_user.save()

    if _leader_group not in api_user.groups.all():
        api_user.groups.add(_leader_group)
        api_user.save()

    leader.api_user = api_user
    leader.save()

    return api_user


def notify_new_leader(leader: Leader) -> None:
    # TODO: implement this!
    pass


def update_leader(leader: Leader, name: str, email: str, phonenumber: str,
                  password: str = None, is_active: bool = True) -> Leader:
    _leader_group = ApiGroup.objects.get(name=settings.LEADER_GROUP)
    _participant_group = ApiGroup.objects.get(name=settings.PARTICIPANT_GROUP)

    leader.name = name
    leader.phonenumber = phonenumber
    leader.save()

    api_user = leader.api_user
    api_user.email = email

    if is_active:
        if _leader_group not in api_user.groups.all():
            api_user.groups.add(_leader_group)

        api_user.is_active = True
    else:
        if _leader_group in api_user.groups.all():
            api_user.groups.remove(_leader_group)

        # The account should still be active if the leader is also a participant
        api_user.is_active = _participant_group in api_user.groups.all()

    if password:
        api_user.set_password(password)

    api_user.save()

    return leader
