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
from django.conf.urls import url, include
from django.views.generic import RedirectView
import dafousers.views
import dafoconfig.views

root_redirect = RedirectView.as_view(
    url=reverse_lazy('admin:index'),
    permanent=False
)

urlpatterns = [
    # Redirect root URL to admin
    # url(r'^$', root_redirect, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('dafoconfig.urls', namespace='dafoconfig')),
    url(r'^', include('dafousers.urls', namespace='dafousers')),
]
