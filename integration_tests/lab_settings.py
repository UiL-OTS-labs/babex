import os
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
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.getenv("DB_HOST") or "localhost",
        "PORT": int(os.getenv("DB_PORT") or 3306),
        "NAME": os.getenv("DB_NAME") or "babex",
        "USER": os.getenv("DB_USER") or "babex",
        "PASSWORD": os.getenv("DB_PASSWORD") or "babex",
    }
}

FIXTURE_DIRS = ['data_fixtures']

ALLOWED_HOSTS = ["localhost"]
DEBUG = True

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"signups": "1000/hour"}
