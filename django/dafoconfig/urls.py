from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.views.i18n import JavaScriptCatalog
import django.contrib.auth.views

import dafoconfig.views as dafo_views

urlpatterns = [
    url(
        r'^$',
        dafo_views.PluginListView.as_view(),
        name='plugin-list'
    ),
    url(
        r'^cvr/config/?$',
        dafo_views.CvrPluginConfigurationView.as_view(),
        name='plugin-cvr-edit'
    ),
    url(
        r'^cpr/config/?$',
        dafo_views.CprPluginConfigurationView.as_view(),
        name='plugin-cpr-edit'
    ),
    url(
        r'^gladdrreg/config/?$',
        dafo_views.GladdregPluginConfigurationView.as_view(),
        name='plugin-gladdrreg-edit'
    ),
]
