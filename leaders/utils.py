from typing import Optional, Tuple
from datetime import datetime, timedelta
import urllib.parse as parse

from django.conf import settings
from django.contrib.auth.models import Group
from pytz import timezone
from cdh.core.utils.mail import send_template_email

from api.auth.ldap_backend import ApiLdapBackend
from api.auth.models import UserToken
from main.models import User
from api.utils import get_reset_links
from main.utils import is_ldap_enabled
from .models import Leader


def create_leader(name: str, email: str, phonenumber: str,
                  password: Optional[str] = None) -> Tuple[Leader, bool]:
    """
    This function creates a new Leader object.

    If the email specified is already used, it will return the Leader object for
    that email.

    If there already is a User object with that email, that one will be
    retrieved and used in the Leader object. This can happen if someone who
    already made an account as a participant is added as a leader.

    If no User object exists, one will be created.

    In both cases the User object is added to the leader group.

    :param name:
    :param email:
    :param phonenumber:
    :param password:
    :return:
    """
    _leader_group = Group.objects.get(name=settings.LEADER_GROUP)
    existing_leader = Leader.objects.filter(user__email=email)

    if existing_leader:
        return existing_leader[0], True

    leader = Leader()
    leader.name = name
    leader.phonenumber = phonenumber

    existing_user = User.objects.get(email=email)
    existing = False

    if existing_user:
        existing = True
        user = existing_user
    else:
        user = User()
        user.email = email

        if password:
            user.set_password(password)

        user.save()

    if _leader_group not in user.groups.all():
        user.groups.add(_leader_group)
        user.save()

    leader.user = user
    leader.save()

    return leader, existing


def create_ldap_leader(name: str, email: str, phonenumber: str) -> Leader:
    """
    This function creates a new Leader object, which will log in through the
    LDAP.

    If the email specified is already used, it will return the Leader object for
    that email.

    If there already is a User object with that email, that one will be
    retrieved and used in the Leader object. That account will NOT be
    updated to use ldap. This can happen if someone who already made an account
     as a participant is added as a leader.

    If no User object exists, one will be created.

    In both cases the User object is added to the leader group.

    :param email:
    :return:
    """
    _leader_group = Group.objects.get(name=settings.LEADER_GROUP)
    existing_leader = Leader.objects.filter(user__email=email)

    if existing_leader:
        return existing_leader[0]

    leader = Leader()
    leader.name = name
    leader.phonenumber = phonenumber

    existing_user = User.objects.get(email=email)

    if existing_user:
        user = existing_user
    else:
        # Create an empty account first, before we populate
        User.objects.create(email=email)
        user = ApiLdapBackend().populate_user(email)

    if _leader_group not in user.groups.all():
        user.groups.add(_leader_group)
        user.save()

    leader.user = user
    leader.save()

    return leader


def get_login_link() -> str:
    return parse.urljoin(
        settings.FRONTEND_URI,
        "login/"
    )


def notify_new_leader(leader: Leader, existing=False) -> None:
    ...


def notify_new_ldap_leader(leader: Leader) -> None:
    subject = 'UiL OTS Experimenten: new account'
    context = {
        'name':             leader.name,
        'email':            leader.user.email,
        'login_link':       get_login_link(),
    }

    send_template_email(
        [leader.user.email],
        subject,
        'leaders/mail/notify_new_ldap_leader',
        context,
        'no-reply@uu.nl'
    )


def _get_tomorrow():
    tz = timezone(settings.TIME_ZONE)
    return datetime.now(tz) + timedelta(hours=24)


def update_leader(leader: Leader, name: str, email: str, phonenumber: str,
                  password: str = None, is_active: bool = True) -> Leader:
    _leader_group = Group.objects.get(name=settings.LEADER_GROUP)
    _participant_group = Group.objects.get(name=settings.PARTICIPANT_GROUP)

    leader.name = name
    leader.phonenumber = phonenumber
    leader.save()

    user = leader.user
    user.email = email

    if is_active:
        if _leader_group not in user.groups.all():
            user.groups.add(_leader_group)

        user.is_active = True
    else:
        if _leader_group in user.groups.all():
            user.groups.remove(_leader_group)

        # The account should still be active if the leader is also a participant
        user.is_active = _participant_group in user.groups.all()

    if password:
        user.set_password(password)

    user.save()

    return leader


def delete_leader(leader: Leader) -> None:
    _leader_group = Group.objects.get(name=settings.LEADER_GROUP)
    _participant_group = Group.objects.get(name=settings.PARTICIPANT_GROUP)

    user = leader.user

    all_groups = user.groups.all()

    if _leader_group in all_groups:
        if len(all_groups) == 1:
            user.delete()
        else:
            user.groups.remove(_leader_group)
            user.is_active = _participant_group in all_groups

            user.is_ldap_account = False

            user.save()

    leader.delete()


def convert_leader_to_ldap(leader: Leader) -> None:
    """All hail the mighty LDAP!
    Oh wait, it's not that kind of conversion... bummer

    Changes an eligible non-ldap-enabled leader account to use ldap for
    authentication
    """
    user = leader.user

    if not is_ldap_enabled() or user.is_ldap_account:
        return

    if not user.email.endswith("uu.nl"):
        return

    user.set_password(None)
    user.is_ldap_account = True
    user.save()

    ApiLdapBackend().populate_user(user.email)
