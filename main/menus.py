from menu import Menu, MenuItem
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

Menu.add_item("home", MenuItem(_('mainmenu:home'),
                               reverse('main:home'),
                               ))


Menu.add_item("footer", MenuItem(_('footermenu:login'),
                                 reverse('main:login'),
                                 check=lambda x: not x.user.is_authenticated
                                 ))

Menu.add_item("footer", MenuItem(_('footermenu:logout'),
                                 reverse('main:logout'),
                                 check=lambda x: x.user.is_authenticated
                                 ))