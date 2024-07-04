from os import getenv

from ppn_backend.settings_base import *

# secrets
SECRET_KEY = secret("SECRET_KEY")
FIELD_ENCRYPTION_KEY = secret("FIELD_ENCRYPTION_KEY")

DEBUG = False
ADMINS = [('Admin', getenv('ADMIN_EMAIL'))]

ALLOWED_HOSTS = [getenv("LAB_SERVER")]
CSRF_TRUSTED_ORIGINS = ["https://" + getenv("LAB_SERVER")]

STATIC_ROOT = "/static"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": getenv("DB_HOST"),
        "NAME": getenv("DB_NAME"),
        "USER": getenv("DB_USER"),
        "PASSWORD": secret("DB_PASSWORD"),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] {name} ({levelname}): {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level':    'INFO',  # DEBUG is possible, but is VERY verbose.
        },
    },
}

MIDDLEWARE += [
    "csp.middleware.CSPMiddleware",
]

FRONTEND_URI = "https://" + getenv("LAB_SERVER") + "/"
PARENT_URI = "https://" + getenv("PARENT_SERVER") + "/"

if not getenv('NO_SAML'):
    try:
        from .saml_settings import enable_saml
        enable_saml(globals())
    except ImportError:
        print("Proceeding without SAML")


# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_FROM = getenv('EMAIL_FROM')
EMAIL_HOST_USER = getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = secret('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

VUE_MANIFEST = "/static/vue/manifest.json"
