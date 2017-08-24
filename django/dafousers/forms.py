# from django.shortcuts import render

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from dafousers.models import PasswordUser, UserProfile

class PasswordUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.HiddenInput()
    )
    user_profiles = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(),
        label="brugerprofiler",
        required=False,
        widget=FilteredSelectMultiple(
            "user_profiles",
            False,
            attrs={'rows':'6'}
        ),
    )

    class Media:
        # Adding this javascript is crucial
        js = ['/admin/jsi18n/']

    class Meta:
        model = PasswordUser
        fields = ['givenname', 'lastname', 'email', 'organisation', 'status']

    def save(self, commit=True):
        return super(PasswordUserForm, self).save(commit=commit)