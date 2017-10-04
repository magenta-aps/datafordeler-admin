from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
import re

# from dafoadmin.dafousers.views import LoginRequiredMixin
from .models import CvrConfig, CprConfig, GladdregConfig
from .forms import CvrConfigurationForm, CprConfigurationForm, GladdrregConfigurationForm

class PluginConfigurationView(UpdateView):

    plugin_name = None

    def get_object(self, queryset=None):
        return self.model.objects.first()

    def get_context_data(self, **kwargs):
        context = {
            'plugin_name': self.plugin_name,
            'sections': self.get_sections()
        }

        context.update(kwargs)
        return super(PluginConfigurationView, self).get_context_data(**context)

    def get_sections(self):
        return [{'items': self.get_form()}]


class CvrPluginConfigurationView(PluginConfigurationView):

    model = CvrConfig
    form_class = CvrConfigurationForm
    template_name = 'form.html'
    plugin_name = 'CVR'


class CprPluginConfigurationView(PluginConfigurationView):

    model = CprConfig
    form_class = CprConfigurationForm
    template_name = 'form.html'
    plugin_name = 'CPR'

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


class GladdregPluginConfigurationView(PluginConfigurationView):

    model = GladdregConfig
    form_class = GladdrregConfigurationForm
    template_name = 'form.html'
    plugin_name = 'Gladdrreg'


class PluginListTable(TemplateView):

    template_name = 'table.html'

    def get_context_data(self, **kwargs):

        list = [
            {
                'name': 'CVR',
                'configlink': reverse('dafoconfig:plugin-cvr-edit')
            },
            {
                'name': 'CPR',
                'configlink': reverse('dafoconfig:plugin-cpr-edit')
            },
            {
                'name': 'Gladdrreg',
                'configlink': reverse('dafoconfig:plugin-gladdrreg-edit')
            },
        ]

        order = self.request.GET.get('order', 'name')
        if order:
            reversed = False
            if order[0] == '-':
                order = order[1:]
                reversed = True
            if order == "name":
                list = sorted(list, key=lambda item: item['name'], reverse=reversed)


        context = {
            'list': list,
            'order': order
        }
        context.update(kwargs)
        return super(PluginListTable, self).get_context_data(**context)


class PluginListView(PluginListTable):

    template_name = 'list.html'
