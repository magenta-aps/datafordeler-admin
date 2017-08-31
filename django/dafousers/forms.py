# from django.shortcuts import render

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from dafousers import models


class PasswordUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.HiddenInput()
    )
    user_profiles = forms.ModelMultipleChoiceField(
        queryset=models.UserProfile.objects.all(),
        label="brugerprofiler",
        required=False,
        widget=FilteredSelectMultiple(
            "user_profiles",
            False,
            attrs={'rows': '6'}
        ),
    )

    class Media:
        # Adding this javascript is crucial
        js = ['/admin/jsi18n/']

    class Meta:
        model = models.PasswordUser
        fields = ['givenname', 'lastname', 'email', 'organisation', 'status']

    def save(self, commit=True):
        return super(PasswordUserForm, self).save(commit=commit)

