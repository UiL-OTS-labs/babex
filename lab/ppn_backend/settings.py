import os
from typing import List

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .saml_settings import enable_saml
from .settings_base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "hk+83s0m6j8(ei)gxgy)e59b@^n77y_bmd4(#yyknr#whcrf^#"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: List[str] = []
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS.append("debug_toolbar")
MIDDLEWARE.append(
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)

FIELD_ENCRYPTION_KEY = "IhWBKI5MORNNtI5WWqZwOflEwojBACtuz9lKXwcF4HI="

FRONTEND_URI = "http://localhost:8000/"
PARENT_URI = "http://localhost:9000/"

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_FROM = "babex@localhost.local"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    },
}

AUTH_PASSWORD_VALIDATORS = []

# Local development server doesn't support https
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

enable_saml(globals())
