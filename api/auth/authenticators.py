from django.core.exceptions import ObjectDoesNotExist
from rest_framework import authentication

from .models import ApiUser
from .token import JwtToken


class JwtAuthentication(authentication.TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, key):
        decoded = JwtToken.validate_token(key)

        user = ApiUser.objects.get(pk=decoded['pk'])

        user.is_authenticated = True

        return (user, decoded)


class PostAuthenticator:

    @classmethod
    def authenticate(cls, username, password, *args, **kwargs):

        try:
            user = ApiUser.objects.get(email=username)
        except ObjectDoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None
