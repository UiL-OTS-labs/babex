from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem


def _user_is_authenticated(x: WSGIRequest) -> bool:
    """
    Checks whether the user x is is_authenticated
    """
    return x.user.is_authenticated


def _user_is_not_authenticated(x: WSGIRequest) -> bool:
    """
    Checks whether the user x is not authenticated
    """
    return not _user_is_authenticated(x)


def _user_is_admin(req: WSGIRequest) -> bool:
    return req.user.is_authenticated and req.user.is_staff


Menu.add_item("home", MenuItem(_("mainmenu:home"), reverse("main:home"), exact_url=True))


Menu.add_item("main", MenuItem(_("mainmenu:agenda"), reverse("agenda:home"), check=_user_is_authenticated))

experiments_menu = [
    MenuItem(_("mainmenu:experiments:overview"), reverse("experiments:home")),
    MenuItem(_("mainmenu:locations"), reverse("experiments:location_home")),
    MenuItem(_("mainmenu:criteria"), reverse("experiments:criteria_home")),
]

Menu.add_item(
    "main", MenuItem(_("mainmenu:experiments"), url=None, check=_user_is_authenticated, children=experiments_menu)
)


users_menu = [
    MenuItem(_("mainmenu:leaders"), reverse("main:users_leaders"), check=_user_is_authenticated),
    MenuItem(_("mainmenu:admins"), reverse("main:users_admins"), check=_user_is_authenticated),
]

Menu.add_item("main", MenuItem(_("mainmenu:users"), check=_user_is_authenticated, children=users_menu, url=None))

participants_menu = [
    MenuItem(_("mainmenu:participants"), reverse("participants:home"), check=_user_is_authenticated),
    MenuItem(_("mainmenu:demographics"), reverse("participants:demographics"), check=_user_is_authenticated),
    MenuItem(_("mainmenu:signups"), reverse("signups:list"), check=_user_is_authenticated),
]

Menu.add_item(
    "main", MenuItem(_("mainmenu:participants"), children=participants_menu, check=_user_is_authenticated, url=None)
)


admin_menu = [MenuItem(_("mainmenu:admin:closings"), reverse("agenda:admin.closings"))]

Menu.add_item("main", MenuItem(_("mainmenu:admin"), children=admin_menu, check=_user_is_admin, url=None))


if "datamanagement" in settings.INSTALLED_APPS:
    Menu.add_item(
        "main", MenuItem(_("mainmenu:datamanagement"), reverse("datamanagement:overview"), check=_user_is_authenticated)
    )


Menu.add_item("footer", MenuItem(_("footermenu:login"), reverse("main:login"), check=_user_is_not_authenticated))

Menu.add_item("footer", MenuItem(_("main:globals:logout"), reverse("main:logout"), check=_user_is_authenticated))
