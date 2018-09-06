import dafoconfig.views as dafo_views
from django.conf.urls import url

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
        r'^plugin/geo/config/?$',
        dafo_views.GeoPluginConfigurationView.as_view(),
        name='plugin-geo-edit'
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

    url(
        r'^plugin/(?P<plugin>[a-z]+)/pull/?$',
        dafo_views.PluginPullView.as_view(),
        name='plugin-pull'
    ),
]
