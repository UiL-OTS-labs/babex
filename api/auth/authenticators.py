from django.core.exceptions import ObjectDoesNotExist
from rest_framework import authentication

from api.auth.ldap_backend import ApiLdapBackend
from .models import ApiUser
from .token import jwt_token


class JwtAuthentication(authentication.TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, key):
        decoded = jwt_token.validate_token(key)

        user = ApiUser.objects.get(pk=decoded['pk'])

        user.is_authenticated = True

        return (user, decoded)


class PostAuthenticator:

    @classmethod
    def authenticate(cls, username, password, *args, **kwargs):
        user = ApiUser.objects.get_by_email(username)

        if not user:
            return None

        # If it's an LDAP account, attempt authentication with the ldap backend
        # Only available for leader accounts
        if user.is_ldap_account and user.is_leader:
            try:
                # For complicated reasons*, we let the LDAP backend recreate our
                # user model
                # * basically, it's easier to do this than to override
                # everything in the backend
                user = ApiLdapBackend().authenticate(username, password)
            except:
                return None

            return user
        # If it's not an ldap account, check the password field
        elif user.check_password(password):
            return user
        else:
            return None

