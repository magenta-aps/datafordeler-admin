from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import UpdateView
import re

from .models import CvrConfig, CprConfig, GladdregConfig
from .forms import CvrConfigurationForm, CprConfigurationForm, GladdrregConfigurationForm


class ConfigurationView(UpdateView):

    plugin_name = None

    def get_object(self, queryset=None):
        return self.model.objects.first()

    def get_context_data(self, **kwargs):
        context = {
            'plugin_name': self.plugin_name,
            'sections': self.get_sections()
        }

        context.update(kwargs)
        return super(ConfigurationView, self).get_context_data(**context)

    def get_sections(self):
        return [{'items': self.get_form()}]


class CvrConfigurationView(ConfigurationView):

    model = CvrConfig
    form_class = CvrConfigurationForm
    template_name = "form.html"
    plugin_name = "CVR"


class CprConfigurationView(ConfigurationView):

    model = CprConfig
    form_class = CprConfigurationForm
    template_name = "form.html"
    plugin_name = "CPR"

    def get_sections(self):
        form = self.get_form()
        regex = re.compile('([a-zA-Z]+register)')
        sections = {}
        for (name, field) in form.fields.items():
            m = regex.match(name)
            key = 'other'
            if m:
                key = m.group(1)
            if not key in sections:
                obj = {'items': []}
                if key != 'other':
                    obj['name'] = key
                sections[key] = obj
            sections[key]['items'].append(form[name])
        return sections.values()


class GladdregConfigurationView(ConfigurationView):

    model = GladdregConfig
    form_class = GladdrregConfigurationForm
    template_name = "form.html"
    plugin_name = "Gladdrreg"
