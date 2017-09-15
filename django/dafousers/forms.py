# -*- coding: utf-8 -*-
# from django.shortcuts import render

from django import forms
from django.contrib.admin import widgets
from django.utils import timezone
from django.utils.translation import ugettext as _
from dafousers import models, model_constants


class PasswordUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.HiddenInput(),
        initial="*"
    )
    user_profiles = forms.ModelMultipleChoiceField(
        queryset=models.UserProfile.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            _(u"brugerprofiler"),
            False,
            attrs={'rows': '6'}
        ),
    )

    class Meta:
        model = models.PasswordUser
        fields = ['givenname', 'lastname', 'email', 'organisation', 'status']

    def __init__(self, *args, **kwargs):
        if 'pk' in kwargs:
            self.pk = kwargs.pop('pk')
            super(PasswordUserForm, self).__init__(*args, **kwargs)
            self.initial['user_profiles'] = models.PasswordUser.objects.get(id=self.pk).user_profiles.all()
        else:
            super(PasswordUserForm, self).__init__(*args, **kwargs)


class CertificateUserForm(forms.ModelForm):

    user_profiles = forms.ModelMultipleChoiceField(
        queryset=models.UserProfile.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            _(u"brugerprofiler"),
            False,
            attrs={'rows': '6'}
        ),
    )

    certificates = forms.ModelMultipleChoiceField(
        queryset=models.CertificateUser.objects.none(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            _(u"certifikater"),
            False,
            attrs={'rows': '6'}
        ),
    )

    certificate_years_valid = forms.ChoiceField(
        required=False,
        choices=model_constants.CertificateUser.certificate_years_valid_choices
    )

    current_time = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        initial=timezone.now().strftime('%Y-%m-%d %H:%M:%S+00:00')
    )

    class Meta:
        model = models.CertificateUser
        fields = ['name', 'identification_mode', 'organisation', 'comment', 'contact_name', 'contact_email']

    def __init__(self, *args, **kwargs):
        if 'pk' in kwargs:
            self.pk = kwargs.pop('pk')
            super(CertificateUserForm, self).__init__(*args, **kwargs)
            self.initial['user_profiles'] = models.CertificateUser.objects.get(id=self.pk).user_profiles.all()
            certs = models.CertificateUser.objects.get(id=self.pk).certificates.all()
            self.fields['certificates'].queryset = certs
            self.initial['certificates'] = certs
        else:
            super(CertificateUserForm, self).__init__(*args, **kwargs)


class IdentityProviderAccountForm(forms.ModelForm):

    user_profiles = forms.ModelMultipleChoiceField(
        queryset=models.UserProfile.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            _(u"brugerprofiler"),
            False,
            attrs={'rows': '6'}
        ),
    )

    class Meta:
        model = models.IdentityProviderAccount
        fields = ['name', 'idp_entity_id', 'idp_type', 'metadata_xml_file', 'metadata_xml', 'organisation',
                  'contact_name', 'contact_email', 'userprofile_attribute', 'userprofile_attribute_format',
                  'userprofile_adjustment_filter_type', 'userprofile_adjustment_filter_value']

    def __init__(self, *args, **kwargs):
        if 'pk' in kwargs:
            self.pk = kwargs.pop('pk')
            super(IdentityProviderAccountForm, self).__init__(*args, **kwargs)
            self.initial['user_profiles'] = models.IdentityProviderAccount.objects.get(id=self.pk).user_profiles.all()
        else:
            super(IdentityProviderAccountForm, self).__init__(*args, **kwargs)


class UserProfileForm(forms.ModelForm):

    system_roles = forms.ModelMultipleChoiceField(
        queryset=models.SystemRole.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            _(u"systemroller"),
            False,
            attrs={'rows': '6'}
        ),
    )

    area_restrictions = forms.ModelMultipleChoiceField(
        queryset=models.AreaRestriction.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            _(u"områdeafgrænsninger"),
            False,
            attrs={'rows': '6'}
        ),
    )

    class Meta:
        model = models.UserProfile
        fields = ['name']

    def __init__(self, *args, **kwargs):
        if 'pk' in kwargs:
            self.pk = kwargs.pop('pk')
            super(UserProfileForm, self).__init__(*args, **kwargs)
            self.initial['system_roles'] = models.UserProfile.objects.get(id=self.pk).system_roles.all()
            self.initial['area_restrictions'] = models.UserProfile.objects.get(id=self.pk).area_restrictions.all()
        else:
            super(UserProfileForm, self).__init__(*args, **kwargs)