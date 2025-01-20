from os import getenv

from parent.settings import *

DEBUG = False
ADMINS = [("Admin", getenv("ADMIN_EMAIL"))]

ALLOWED_HOSTS = [getenv("PARENT_SERVER")]
CSRF_TRUSTED_ORIGINS = ["https://" + getenv("PARENT_SERVER")]

STATIC_ROOT = "/static"

API_HOST = "https://" + getenv("LAB_SERVER")
JWT_SECRET = secret("JWT_SECRET")


# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_FROM = getenv("EMAIL_FROM")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = secret("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

VUE_MANIFEST = "/static/vue/.vite/manifest.json"


# Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False
X_FRAME_OPTIONS = "DENY"


# Django CSP
# http://django-csp.readthedocs.io/en/latest/index.html
CSP_REPORT_ONLY = False
CSP_UPGRADE_INSECURE_REQUESTS = True
CSP_INCLUDE_NONCE_IN = ["script-src"]

CSP_DEFAULT_SRC = [
    "'self'",
]
CSP_SCRIPT_SRC = [
    "'self'",
]
CSP_FONT_SRC = [
    "'self'",
    "data:",
]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = [
    "'self'",
    "data:",
]

MIDDLEWARE += [
    "csp.middleware.CSPMiddleware",
]
