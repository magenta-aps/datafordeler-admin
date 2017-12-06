# -*- coding: utf-8 -*-
import datetime
import json

import fancy_cronfield.fields
from django.forms import ModelForm as ModelForm
from django.forms.widgets import Textarea

from .models import CvrConfig, CprConfig, DumpConfig, GladdregConfig, Command


class ConfigurationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ConfigurationForm, self).__init__(*args, **kwargs)

    def _cronfield_changed(self):
        return any(isinstance(self.instance._meta.get_field(field_name),
                              fancy_cronfield.fields.CronField)
                   for field_name in self.changed_data)

    def save(self, commit=True):
        instance = super(ConfigurationForm, self).save(commit)

        if self._cronfield_changed():
            Command(
                commandname="schedule-changed",
                commandbody=json.dumps(
                    {
                        'table': self.instance._meta.db_table,
                        'fields': self.changed_data,
                        'id': self.instance.id,
                    }),
                issuer="admin interface",
                received=datetime.datetime.now(),
                status=Command.STATUS_QUEUED,
            ).save()

        return instance


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


class DumpConfigurationForm(ConfigurationForm):
    class Meta:
        model = DumpConfig
        exclude = ['id']

    widgets = {
        'schedule': fancy_cronfield.widgets.CronWidget(
            options={'use_gentle_select': True}
        ),
    }
