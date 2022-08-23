import enum
from typing import Optional

import jwt
from django.conf import settings
from django.core import exceptions


class Algorithms(enum.Enum):
    SHA = 'HS512'
    RSA = 'RSA512'


class JwtToken:

    def __init__(self):
        self._algorithm: Optional[enum.Enum] = None
        self._encode_key: Optional[str] = None
        self._decode_key: Optional[str] = None

        if hasattr(settings, 'JWT_ALGORITHM'):
            self._algorithm = Algorithms(settings.JWT_ALGORITHM)
        else:
            raise exceptions.ImproperlyConfigured('JWT_ALGORITHM not set!')

        if self._algorithm == Algorithms.RSA:
            with open(settings.JWT_PRIVATE_KEY, 'r') as key_file:
                self._encode_key = key_file.read()

            with open(settings.JWT_PUBLIC_KEY, 'r') as key_file:
                self._decode_key = key_file.read()

        elif self._algorithm == Algorithms.SHA:
            self._encode_key = settings.SECRET_KEY
            self._decode_key = settings.SECRET_KEY

    def validate_token(self, token):
        if self._decode_key is None:
            raise exceptions.ImproperlyConfigured('no decode key!')

        try:
            decoded = jwt.decode(token, self._decode_key, algorithms=[self._algorithm.value] if self._algorithm else [])
        except jwt.DecodeError:
            return None

        return decoded

    def make_token(self, user):
        if self._encode_key is None:
            raise exceptions.ImproperlyConfigured('no encode key!')

        payload = {
            "pk": user.pk
        }

        return jwt.encode(payload, self._encode_key, algorithm=self._algorithm.value if self._algorithm else None)


jwt_token = JwtToken()
