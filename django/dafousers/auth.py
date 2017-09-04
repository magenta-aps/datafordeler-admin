# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dafousers.models import PasswordUser
from dafousers.models import UserProfile
from dafousers.models import SystemRole
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in


class DafoUsersAuthBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            pwuser = PasswordUser.objects.get(email=username)
            if not pwuser.check_password(password):
                return None
        except PasswordUser.DoesNotExist:
            pwuser = None

        if pwuser:
            try:
                djangouser = User.objects.get(email=pwuser.email)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                # because only the password PasswordUser is checked.
                djangouser = User(
                    username=pwuser.email,
                    email=pwuser.email,
                )
                djangouser.save()

            return djangouser

        return None

    def get_user(user_id):
        try:
            pwuser = PasswordUser.objects.get(email=username)
        except PasswordUser.DoesNotExist:
            return None

        try:
            return User.objects.get(email=pwuser.email)
        except User.DoesNotExist:
            pass

        return None


def get_auth_info(request):
    if hasattr(request, '_dafoauthinfo'):
        return request._dafoauthinfo

    info = None

    # TODO: Fetch info from token data if authenticated with saml2

    if hasattr(request, 'user') and request.user.is_authenticated():
        try:
            pwuser = PasswordUser.objects.get(email=request.user.email)
            info = DafoAuthInfo(pwuser.user_profiles.all())
        except PasswordUser.DoesNotExist:
            info = None

    request._dafoauthinfo = info
    return info


class DafoAuthInfo(object):
    user_profiles_qs = None
    system_roles_qs = None

    def __init__(self, profiles_queryset=UserProfile.objects.none()):
        self.user_profiles_qs = profiles_queryset
        self.system_roles_qs = SystemRole.objects.filter(
            userprofile__in=self.user_profiles
        )

    def has_user_profile(self, name):
        return self.user_profiles_qs.filter(
            name=name
        ).exists()

    def has_system_role(self, name):
        return self.system_roles_qs.filter(
            name=name
        ).exists()

    @property
    def user_profiles(self):
        return self.user_profiles_qs.all()

    @property
    def system_roles(self):
        return self.system_roles_qs.all()

    @property
    def admin_user_profiles(self):
        if self.has_user_profile("DAFO Administrator"):
            return UserProfile.objects.all()
        elif self.has_user_profile("DAFO Serviceudbyder"):
            return self.user_profiles_qs
        else:
            return UserProfile.objects.none()

    @property
    def admin_system_roles(self):
        if self.has_user_profile("DAFO Administrator"):
            return SystemRole.objects.all()
        elif self.has_user_profile("DAFO Serviceudbyder"):
            return self.system_roles_qs
        else:
            return SystemRole.objects.none()
