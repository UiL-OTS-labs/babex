from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.hashers import check_password

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

        if check_password(password, user.password):
            return user

        return None
