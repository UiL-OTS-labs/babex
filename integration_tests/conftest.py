from collections import namedtuple
import importlib
import os
import pytest
import subprocess
import email
import glob
import shutil

import django
from lab_settings import EMAIL_FILE_PATH

LAB_PORT = 18000
PARENT_PORT = 19000


class DjangoServerProcess:
    def __init__(self, name, path, port):
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = "."
        self.name = name
        self.path = path
        self.port = port
        self.settings = f"{name}_settings"

    def migrate(self):
        # delete existing db
        try:
            os.unlink(f"{self.name}.int.db.sqlite3")
        except FileNotFoundError:
            pass

        cmd = [
            "python",
            "-m",
            "django",
            "migrate",
            "--noinput",
            "--settings",
            self.settings,
        ]
        process = subprocess.run(cmd, env=self.env)

        if process.returncode != 0:
            raise RuntimeError(f"could not migrate app in {self.path}")

    def load(self, path):
        """load a data fixture"""
        cmd = [
            "python",
            "-m",
            "django",
            "loaddata",
            path,
            "--settings",
            self.settings,
        ]
        process = subprocess.run(cmd, env=self.env)

        if process.returncode != 0:
            raise RuntimeError(f"could not load data from {path}")

    def start(self):
        cmd = [
            "python",
            "-m",
            "django",
            "runserver",
            str(self.port),
            "--settings",
            self.settings,
        ]
        self.process = subprocess.Popen(cmd, env=self.env)
        try:
            self.process.wait(1)
        except subprocess.TimeoutExpired:
            # this is good, the process is still running
            pass

        if self.process.returncode is not None:
            raise RuntimeError(f"could not start app in {self.path}")

    def shutdown(self):
        self.process.terminate()

    @property
    def url(self):
        return f"http://localhost:{self.port}/"

    def get_model(self, app_name: str, model: str):
        os.environ['DJANGO_SETTINGS_MODULE'] = self.settings
        django.setup()
        module = importlib.import_module(f'{app_name}.models')
        return module.__dict__[model]


@pytest.fixture(scope="module")
def lab_app():
    server = DjangoServerProcess("lab", "../lab", LAB_PORT)
    server.migrate()
    server.start()
    yield server
    server.shutdown()


@pytest.fixture(scope="module")
def parent_app():
    server = DjangoServerProcess("parent", "../parent", PARENT_PORT)
    server.migrate()
    server.start()
    yield server
    server.shutdown()


@pytest.fixture(scope="module")
def apps(lab_app, parent_app):
    return namedtuple("Apps", "lab,parent")(lab_app, parent_app)


@pytest.fixture
def as_admin(sb, lab_app):
    lab_app.load("admin")
    driver = sb.get_new_driver()
    sb.switch_to_driver(driver)
    sb.open(lab_app.url)
    sb.type("#id_username", "admin")
    sb.type("#id_password", "admin")
    sb.click('button:contains("Log in")')
    sb.switch_to_default_driver()
    return driver


def read_mail(address):
    messages = []
    for path in glob.glob(EMAIL_FILE_PATH + "/*"):
        with open(path) as f:
            msg = email.message_from_file(f)
            if msg["To"] == address:
                messages.append(msg)

    return messages


@pytest.fixture
def mailbox():
    yield read_mail
    # delete emails
    shutil.rmtree(EMAIL_FILE_PATH)


@pytest.fixture(scope="function", autouse=True)
def _dj_autoclear_mailbox() -> None:
    # Override the `_dj_autoclear_mailbox` test fixture in `pytest_django`.
    pass
