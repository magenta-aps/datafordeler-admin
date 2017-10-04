from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.views.i18n import JavaScriptCatalog
import django.contrib.auth.views

import dafoconfig.views as dafo_views

urlpatterns = [
    url(
        r'^plugin/?$',
        dafo_views.PluginListView.as_view(),
        name='plugin-list'
    ),
    url(
        r'^plugin/cvr/config/?$',
        dafo_views.CvrPluginConfigurationView.as_view(),
        name='plugin-cvr-edit'
    ),
    url(
        r'^plugin/cpr/config/?$',
        dafo_views.CprPluginConfigurationView.as_view(),
        name='plugin-cpr-edit'
    ),
    url(
        r'^plugin/gladdrreg/config/?$',
        dafo_views.GladdregPluginConfigurationView.as_view(),
        name='plugin-gladdrreg-edit'
    ),
    url(
        r'^ajax/update_plugin_queryset/$',
        dafo_views.PluginListTable.as_view(),
        name='update_plugin_queryset'
    ),
]
