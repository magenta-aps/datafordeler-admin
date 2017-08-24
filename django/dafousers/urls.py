from django.conf.urls import url
import dafousers.views as dafo_views

urlpatterns = [
    url(r'user/(?P<pk>[0-9]+)/$',
        dafo_views.PasswordUserDetails.as_view(),
        name='passworduser-details'),
    url(r'user/add/$',
        dafo_views.PasswordUserCreate.as_view(),
        name='passworduser-add'),
    url(r'user/$',
        dafo_views.PasswordUserList.as_view(),
        name='passworduser-list'),
    url(r'^$', dafo_views.IndexView.as_view(), name="index")
]