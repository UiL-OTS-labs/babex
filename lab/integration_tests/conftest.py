import pytest

from main.models import User
from leaders.models import Leader


@pytest.fixture
def admin_user(db):
    admin = User.objects.create(username='admin',
                                is_superuser=True,
                                is_staff=True)
    Leader.objects.create(name='Admin McAdmin',
                          phonenumber='12345678',
                          user=admin)
    admin.set_password('admin')
    admin.save()
    yield admin


@pytest.fixture
def as_admin(sb, admin_user, live_server):
    sb.open(live_server.url)
    # sb.click('#djHideToolBarButton')
    sb.type('#id_username', 'admin')
    sb.type('#id_password', 'admin')
    sb.click('button:contains("Log in")')
