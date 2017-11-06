# -*- coding: utf-8 -*-

from django.forms import ModelForm as ModelForm
from django.forms.widgets import Textarea

from .models import CvrConfig, CprConfig, GladdregConfig


class ConfigurationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ConfigurationForm, self).__init__(*args, **kwargs)


class CvrConfigurationForm(ConfigurationForm):

    class Meta:
        model = CvrConfig
        exclude = ['id']
        widgets = {
            'companyregisterquery': Textarea(),
            'companyunitregisterquery': Textarea(),
            'participantregisterquery': Textarea()
        }


class CprConfigurationForm(ConfigurationForm):

    class Meta:
        model = CprConfig
        exclude = ['id']


class GladdrregConfigurationForm(ConfigurationForm):

    class Meta:
        model = GladdregConfig
        exclude = ['id']
