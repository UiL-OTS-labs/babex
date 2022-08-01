import os
import pytest

from seleniumbase import BaseCase

URL = 'http://localhost:' + os.getenv('TEST_PORT', '9000')


@pytest.fixture
def as_admin(sb):
    sb.open(URL)
    sb.click('#djHideToolBarButton')
    sb.type('#id_username', 'admin')
    sb.type('#id_password', 'admin')
    sb.click('button:contains("Log in")')
