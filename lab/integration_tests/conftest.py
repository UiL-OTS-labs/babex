import pytest


@pytest.fixture
def as_admin(sb, admin_user, live_server):
    sb.open(live_server.url)
    # sb.click('#djHideToolBarButton')
    sb.type("#id_username", "admin")
    sb.type("#id_password", "admin")
    sb.click('button:contains("Log in")')


@pytest.fixture
def as_leader(sb, django_user_model, live_server):
    username = "test_user"
    password = "test_user"
    user = django_user_model.objects.create_user(username=username, password=password)
    sb.open(live_server.url)
    # sb.click('#djHideToolBarButton')
    sb.type("#id_username", username)
    sb.type("#id_password", password)
    sb.click('button:contains("Log in")')
    yield user
