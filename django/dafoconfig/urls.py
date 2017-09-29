from django.conf.urls import url

import dafoconfig.views as dafo_views

urlpatterns = [

    url(r'^config/cvr/$',
        dafo_views.CvrConfigurationView.as_view(),
        name='cvrconfiguration-edit'),
    url(r'^config/cpr/$',
        dafo_views.CprConfigurationView.as_view(),
        name='cvrconfiguration-edit'),
    url(r'^config/gladdrreg/$',
        dafo_views.GladdregConfigurationView.as_view(),
        name='cvrconfiguration-edit'),
]
