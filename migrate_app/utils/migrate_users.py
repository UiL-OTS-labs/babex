from django.conf import settings
from django.contrib.auth import get_user_model

from api.auth.models import ApiGroup, ApiUser
from leaders.models import Leader
from main.hashers import PBKDF2WrappedMD5PasswordHasher
from ..models import Admin, Leaders


def migrate_admins():
    admins = Admin.objects.all()
    user_model = get_user_model()

    for admin in admins:
        if user_model.objects.filter(username=admin.username).exists():
            print("\nAdmin with username {} already exists in the new DB! "
                  "Skipping...".format(admin.username))
            continue

        new_object = user_model()
        new_object.username = admin.username

        new_object.password = _rehash_password(admin.password)

        new_object.save()


def migrate_leaders():
    leaders = Leaders.objects.all()
    leader_group = ApiGroup.objects.get(name=settings.LEADER_GROUP)

    for leader in leaders:
        if ApiUser.objects.filter(email=leader.email).exists():
            print("\nLeader with username {} already exists in the new DB! "
                  "Skipping...".format(leader.email))
            continue

        new_user_object = ApiUser()
        new_leader_object = Leader()

        new_user_object.email = leader.email
        new_user_object.password = _rehash_password(leader.password)
        new_user_object.save()

        new_user_object.groups.add(leader_group)
        new_user_object.save()

        new_leader_object.name = leader.name
        new_leader_object.phonenumber = leader.phonenumber
        new_leader_object.api_user = new_user_object
        new_leader_object.save()


def _rehash_password(password: str) -> str:
    password_hasher = PBKDF2WrappedMD5PasswordHasher()

    return password_hasher.encode_md5_hash(
        password,
        password_hasher.salt(),
    )
