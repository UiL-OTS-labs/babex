import sys
import base64
sys.path.append('../lab')

from ppn_backend.settings_base import *

SECRET_KEY = "something else"
FIELD_ENCRYPTION_KEY = base64.b64encode(b"a" * 32)
PARENT_URI = 'http://localhost:19000/'

DEBUG = True
FIELD_ENCRYPTION_KEY = base64.b64encode(b'a' * 32)

SECRET_KEY = 'secret'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/babex-mailbox'
EMAIL_FROM = "babex@localhost.local"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "lab.int.db.sqlite3",
    },
}

FIXTURE_DIRS = ['data_fixtures']

ALLOWED_HOSTS = ["localhost"]
DEBUG = True
