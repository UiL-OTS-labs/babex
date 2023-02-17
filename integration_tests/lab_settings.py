import sys
sys.path.append('../lab')

from ppn_backend.settings import *

PARENT_URI = 'http://localhost:19000/'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/babex-mailbox'

DATABASES['default']['NAME'] = 'lab.int.db.sqlite3'

FIXTURE_DIRS = ['data_fixtures']
