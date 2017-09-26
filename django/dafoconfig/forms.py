# -*- coding: utf-8 -*-

from django.forms import ModelForm as ModelForm
from django import forms

from .models import CvrConfig


class ConfigurationForm(ModelForm):
    pass


class CvrConfigurationForm(ConfigurationForm):

    class Meta:
        model = CvrConfig
        exclude = []