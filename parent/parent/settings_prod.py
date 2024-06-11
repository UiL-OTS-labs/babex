from os import getenv

from parent.settings import *

DEBUG = False
ADMINS = [("Admin", getenv("ADMIN_EMAIL"))]

ALLOWED_HOSTS = [getenv("PARENT_SERVER")]
CSRF_TRUSTED_ORIGINS = ["https://" + getenv("PARENT_SERVER")]

STATIC_ROOT = "/static"

API_HOST = getenv("LAB_SERVER")


# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_FROM = getenv("EMAIL_FROM")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = secret("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

VUE_MANIFEST = "/static/vue/manifest.json"
