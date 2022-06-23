from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

Menu.add_item("home", MenuItem(_('mainmenu:home'),
                               reverse('main:home'),
                               exact_url=True
                               ))

Menu.add_item("main", MenuItem(_('mainmenu:agenda'),
                               reverse('agenda:home'),
                               check=lambda x: x.user.is_authenticated
                               ))

experiments_menu = [
    MenuItem(_('mainmenu:experiments:overview'),
             reverse('experiments:home')),
    MenuItem(_('mainmenu:locations'),
             reverse('experiments:location_home')),
    MenuItem(_('mainmenu:criteria'),
             reverse('experiments:criteria_home')),
]

Menu.add_item("main", MenuItem(_('mainmenu:experiments'),
                               url=None,
                               check=lambda x: x.user.is_authenticated,
                               children=experiments_menu
                               ))


users_menu = [
    MenuItem(_('mainmenu:leaders'),
             reverse('leaders:home'),
             check=lambda x: x.user.is_authenticated),
    MenuItem(_('mainmenu:admins'),
             reverse('main:users_home'),
             check=lambda x: x.user.is_authenticated)
]

Menu.add_item("main", MenuItem(_('mainmenu:users'),
                               check=lambda x: x.user.is_authenticated,
                               children=users_menu,
                               url=None
                               ))

Menu.add_item("main", MenuItem(_('mainmenu:participants'),
                               reverse('participants:home'),
                               check=lambda x: x.user.is_authenticated
                               ))

# Menu.add_item("main", MenuItem(_('mainmenu:comments'),
#                                reverse('comments:home'),
#                                check=lambda x: x.user.is_authenticated
#                                ))


if 'datamanagement' in settings.INSTALLED_APPS:
    Menu.add_item("main", MenuItem(_('mainmenu:datamanagement'),
                                   reverse('datamanagement:overview'),
                                   check=lambda x: x.user.is_authenticated
                                   ))


Menu.add_item("footer", MenuItem(_('footermenu:login'),
                                 reverse('main:login'),
                                 check=lambda x: not x.user.is_authenticated
                                 ))

Menu.add_item("footer", MenuItem(_('main:globals:logout'),
                                 reverse('main:logout'),
                                 check=lambda x: x.user.is_authenticated
                                 ))
