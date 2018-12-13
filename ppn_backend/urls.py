"""ppn_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('main.urls')),
    path('experiments/', include('experiments.urls')),
    path('leaders/', include('leaders.urls')),
    path('participants/', include('participants.urls')),
    path('comments/', include('comments.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

admin.site.site_header = 'Proefpersonen systeem BACKEND'
admin.site.site_title = 'Proefpersonen systeem BACKEND'
admin.site.index_title = 'Proefpersonen systeem BACKEND'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
