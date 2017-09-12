# from django.shortcuts import render

from django import forms
from django.contrib.admin import widgets
from dafousers import models


class PasswordUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.HiddenInput(),
        initial="*"
    )
    user_profiles = forms.ModelMultipleChoiceField(
        queryset=models.UserProfile.objects.all(),
        label="brugerprofiler",
        required=False,
        widget=widgets.FilteredSelectMultiple(
            "user_profiles",
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
        label="brugerprofiler",
        required=False,
        widget=widgets.FilteredSelectMultiple(
            "user_profiles",
            False,
            attrs={'rows': '6'}
        ),
    )

    class Meta:
        model = models.CertificateUser
        fields = ['name', 'identification_mode', 'organisation', 'comment', 'contact_name', 'contact_email']

    def __init__(self, *args, **kwargs):
        if 'pk' in kwargs:
            self.pk = kwargs.pop('pk')
            super(CertificateUserForm, self).__init__(*args, **kwargs)
            self.initial['user_profiles'] = models.CertificateUser.objects.get(id=self.pk).user_profiles.all()
        else:
            super(CertificateUserForm, self).__init__(*args, **kwargs)
