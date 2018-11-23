from rest_framework import authentication

from .token import JwtToken
from .models import ApiUser


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

        user = ApiUser.objects.get(email=username)

        if user.check_password(password):
            return user

        return None
