import jwt


class JwtToken:

    def __init__(self):
        self._key = 'broodje_kaas'
        #self._algorithm = "RS512"
        self._algorithm = "HS512"

        # with open('jwtRS256.key', 'r') as keyfile:
        #     self._private_key = keyfile.read()
        #
        # with open('jwtRS256.key.pub', 'r') as keyfile:
        #     self._public_key = keyfile.read()

    def validate_token(self, token):
        try:
            decoded = jwt.decode(token, self._key, algorithms=[self._algorithm])
        except jwt.DecodeError:
            return None

        return decoded

    def make_token(self, user):
        payload = {
            "pk": user.pk
        }

        return jwt.encode(payload, self._key, algorithm=self._algorithm)


JwtToken = JwtToken()
