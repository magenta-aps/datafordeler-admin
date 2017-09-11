from django.conf.urls import url
import dafousers.views as dafo_views
import django.contrib.auth.views

urlpatterns = [

    # USER
    url(r'user/(?P<pk>[0-9]+)/$',
        dafo_views.PasswordUserEdit.as_view(),
        name='passworduser-edit'),
    url(r'user/(?P<pk>[0-9]+)/history/$',
        dafo_views.PasswordUserHistory.as_view(),
        name='passworduser-history'),
    url(r'user/add/$',
        dafo_views.PasswordUserCreate.as_view(),
        name='passworduser-add'),
    url(r'user/list/$',
        dafo_views.PasswordUserList.as_view(),
        name='passworduser-list'),

    # SYSTEM
    url(r'system/add/$',
        dafo_views.CertificateUserCreate.as_view(),
        name='certificateuser-add'),
    #url(r'system/list/$',
    #    dafo_views.CertificateUserList.as_view(),
    #    name='certificateuser-list'),

    url(r'frontpage/$',
        dafo_views.FrontpageView.as_view(),
        name="frontpage"),
    url(r'^$',
        dafo_views.IndexView.as_view(),
        name="index"),
    url(r'^login/',
        django.contrib.auth.views.login,
        {'template_name': 'dafousers/login.html', 'redirect_authenticated_user': True},
        name='login'
        ),

    # AJAX Calls
    url(r'^ajax/search_org_user_system/$',
        dafo_views.search_org_user_system,
        name='search_org_user_system'),
    url(r'^ajax/search_user_profile/$',
        dafo_views.search_user_profile,
        name='search_user_profile'),
    url(r'^ajax/update_passworduser_queryset/$',
        dafo_views.update_passworduser_queryset,
        name='update_passworduser_queryset'),
    url(r'^ajax/update_passworduser/$',
        dafo_views.update_passworduser,
        name='update_passworduser'),
]
