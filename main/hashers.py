import hashlib

from django.contrib.auth.hashers import (BasePasswordHasher,
                                         PBKDF2PasswordHasher, )


class UnsaltedMD5PasswordHasher(BasePasswordHasher):
    """
    The Salted MD5 password hashing algorithm (not recommended)
    """
    algorithm = "md5"

    def encode(self, password, _):
        assert password is not None
        return hashlib.md5(bytes(password, 'utf8')).hexdigest()


class PBKDF2WrappedMD5PasswordHasher(PBKDF2PasswordHasher):
    algorithm = 'pbkdf2_wrapped_md5'

    def encode_md5_hash(self, md5_hash, salt, iterations=None):
        return super().encode(md5_hash, salt, iterations)

    def encode(self, password, salt, iterations=None):
        md5_hash = UnsaltedMD5PasswordHasher().encode(password, None)
        return self.encode_md5_hash(md5_hash, salt, iterations)

