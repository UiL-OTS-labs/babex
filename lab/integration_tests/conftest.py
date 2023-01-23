import pytest

from main.models import User


@pytest.fixture
def admin_user(db):
    admin = User.objects.create(username='admin',
                                is_superuser=True,
                                is_staff=True,
                                name='Admin McAdmin',
                                phonenumber='12345678')
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


@pytest.fixture
def as_leader(sb, django_user_model, live_server):
    username = 'test_user'
    password = 'test_user'
    user = django_user_model.objects.create_user(username=username,
                                                 password=password)
    leader = Leader.objects.create(user=user, name='Test Leader')
    sb.open(live_server.url)
    # sb.click('#djHideToolBarButton')
    sb.type('#id_username', username)
    sb.type('#id_password', password)
    sb.click('button:contains("Log in")')
    yield leader
