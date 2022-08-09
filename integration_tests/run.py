# run this from the project root folder with PYTHONPATH=.

import django
import os
import signal
import subprocess
import sys
import time

import settings as test_settings
import pytest


def prepare_clean_db():
    os.unlink(test_settings.DATABASES['default']['NAME'])
    p = subprocess.Popen('python manage.py migrate'.split())
    p.wait()


def create_admin_user():
    from main.models import User
    admin = User.objects.create(username='admin', is_superuser=True)
    admin.set_password('admin')
    admin.save()


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'integration_tests.settings'

    prepare_clean_db()
    django.setup()
    create_admin_user()

    server = subprocess.Popen('python manage.py runserver 12345'.split(),
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    time.sleep(1)

    os.environ['TEST_PORT'] = str(12345)
    pytest.main(['--rootdir=integration_tests'] + sys.argv[1:])

    server.send_signal(signal.SIGINT)
    server.wait()


if __name__ == '__main__':
    main()
