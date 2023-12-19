import sys
sys.path.append('../parent')

from parent.settings import *
from django.utils.translation import gettext_lazy as _

API_HOST = 'http://localhost:18000/'

DATABASES['default']['NAME'] = 'parent.int.db.sqlite3'

LANGUAGES = (
    ("en", _("lang:en")),
)