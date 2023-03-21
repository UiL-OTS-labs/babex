import sys
sys.path.append('../parent')

from parent.settings import *

API_HOST = 'http://localhost:18000/'

DATABASES['default']['NAME'] = 'parent.int.db.sqlite3'
