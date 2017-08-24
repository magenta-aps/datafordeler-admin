from django.conf.urls import url
from dafousers.views import PasswordUserCreate, PasswordUserList, PasswordUserDetails

urlpatterns = [
    url(r'passworduser/(?P<pk>[0-9]+)/$', PasswordUserDetails.as_view(), name='passworduser-details'),
    url(r'passworduser/add/$', PasswordUserCreate.as_view(), name='passworduser-add'),
    url(r'passworduser/$', PasswordUserList.as_view(), name='passworduser-list'),
]