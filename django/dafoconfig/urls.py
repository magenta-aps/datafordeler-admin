from django.conf.urls import url

import dafoconfig.views as dafo_views

urlpatterns = [

    url(r'^config/(?P<plugin>[a-z]+)/$',
        dafo_views.CvrConfigurationView.as_view(),
        name='cvrconfiguration-edit'),
]