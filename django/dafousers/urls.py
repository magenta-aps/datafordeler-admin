from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
import dafousers.views as dafo_views
import django.contrib.auth.views

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
    url(r'frontpage/$', csrf_exempt(dafo_views.FrontpageView.as_view()), name="frontpage"),
    url(r'^$', dafo_views.IndexView.as_view(), name="index"),
    url(r'^login/', csrf_exempt(dafo_views.LoginView.as_view()), name='login'),
    url(r'^logout/', django.contrib.auth.views.logout,
        {'template_name': 'dafousers/logged_out.html'},
        name='logout'),
]
