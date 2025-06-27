import os
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Django extensions
    "django_extensions",
    "vue3_tag",
    # django-simple-menu
    "menu",
    # DRF
    "rest_framework",
    # Impersonate
    "impersonate",
    # local apps
    "cdh.core",
    "cdh.files",
    "cdh.mail",
    "cdh.vue",
    "main",
    "experiments",
    "participants",
    "comments",
    "auditlog",
    "agenda",
    "mailauth",
    "signups",
    "survey_admin",
    "django.contrib.admin",
    "django.forms",
    "django_json_widget",
    # deprecated
    "leaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cdh.core.middleware.ThreadLocalUserMiddleware",
    "mailauth.middleware.SessionTokenMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "ppn_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ppn_backend.wsgi.application"

AUTH_USER_MODEL = "main.User"

LOGIN_URL = reverse_lazy("main:login")

LOGIN_REDIRECT_URL = reverse_lazy("main:home")

SESSION_COOKIE_NAME = "sessionid_admin"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": (),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"signups": "10/hour"},
}

REST_PERMITTED_CLIENTS = ["127.0.0.1"]

JWT_SECRET = "jwt_secret"
JWT_ALGORITHM = "HS512"


# Groups
LEADER_GROUP = "leader"
PARTICIPANT_GROUP = "participant"


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


DATABASE_ROUTERS = [
    "ppn_backend.db_router.DatabaseRouter",
]

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "cdh.core.hashers.PBKDF2WrappedMD5PasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "nl"
LANGUAGES = (
    ("nl", _("lang:nl")),
    ("en", _("lang:en")),
)

TIME_ZONE = "Europe/Amsterdam"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"

# Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
LANGUAGE_COOKIE_SECURE = True

LANGUAGE_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

LANGUAGE_COOKIE_SAMESITE = "strict"

SECURE_SSL_REDIRECT = False
X_FRAME_OPTIONS = "DENY"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

MENU_SELECT_PARENTS = True
MENU_HIDE_EMPTY = False

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

CSP_FRAME_ANCESTORS = ["none"]

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours
VUE_MANIFEST = BASE_DIR / "main/static/vue/.vite/manifest.json"
VUE_URL = "/static/vue/"


# used for loading secrets when deployed with docker
def secret(name):
    path = Path("/run/secrets") / name
    return path.read_text().strip()
