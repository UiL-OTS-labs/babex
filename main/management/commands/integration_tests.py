import time
import os
import sys
import subprocess
import signal

from django.core.management.base import BaseCommand
from django.core.management import call_command
import pytest


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        p = subprocess.Popen('python manage.py runserver 12345'.split(),
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        time.sleep(1)

        os.environ['TEST_PORT'] = str(12345)
        pytest.main(['--rootdir=integration-tests'])

        p.send_signal(signal.SIGINT)
