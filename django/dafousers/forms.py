# -*- coding: utf-8 -*-
# from django.shortcuts import render

from django import forms
from django.contrib.admin import widgets
from django.utils import timezone
from django.utils.translation import ugettext as _
from dafousers import models, model_constants


class AccessAccountForm(forms.ModelForm):

    user_profiles = forms.ModelMultipleChoiceField(
        queryset=models.UserProfile.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            _(u"brugerprofiler"),
            False,
            attrs={'rows': '6'}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(AccessAccountForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['user_profiles'] = self.Meta.model.objects.get(
                id=self.instance.pk
            ).user_profiles.all()
        else:
            super(AccessAccountForm, self).__init__(*args, **kwargs)

        self.fields["user_profiles"].queryset = \
            self.user.dafoauthinfo.admin_user_profiles

    def clean(self):
        super(AccessAccountForm, self).clean()
        if self.instance.pk is not None:
            self.instance.user_profiles = \
                self.instance.get_updated_user_profiles(
                    self.user, self.cleaned_data['user_profiles']
                )


class PasswordUserForm(AccessAccountForm):
    password = forms.CharField(
        widget=forms.HiddenInput(),
        initial="*"
    )

    class Meta:
        model = models.PasswordUser
        fields = ['givenname', 'lastname', 'email', 'organisation', 'status']


class CertificateUserForm(AccessAccountForm):

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
        fields = [
            'name', 'identification_mode', 'organisation', 'comment',
            'contact_name', 'contact_email'
        ]

    def __init__(self, *args, **kwargs):
        super(CertificateUserForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            certs = models.CertificateUser.objects.get(
                id=self.instance.pk
            ).certificates.all()
            self.fields['certificates'].queryset = certs
            self.initial['certificates'] = certs


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
        user = kwargs.pop("user")
        if 'pk' in kwargs:
            self.pk = kwargs.pop('pk')
            super(IdentityProviderAccountForm, self).__init__(*args, **kwargs)
            self.initial['user_profiles'] = models.IdentityProviderAccount.objects.get(id=self.pk).user_profiles.all()
        else:
            super(IdentityProviderAccountForm, self).__init__(*args, **kwargs)

        self.fields["user_profiles"].queryset = \
            user.dafoauthinfo.admin_user_profiles


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