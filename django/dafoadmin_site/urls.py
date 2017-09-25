# -*- coding: utf-8 -*-
"""dafoadmin_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.conf.urls import url, include
from django.views.generic import RedirectView
import dafousers.views

root_redirect = RedirectView.as_view(
    url=reverse_lazy('admin:index'),
    permanent=False
)

urlpatterns = [
    url(r'^', include('dafousers.urls', namespace='dafousers')),
]

if settings.ENABLE_DJANGO_ADMIN:
    urlpatterns = [url(r'^admin/', admin.site.urls)] + urlpatterns