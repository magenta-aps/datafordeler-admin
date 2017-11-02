# -*- coding: utf-8 -*-

import json
import re

import requests
from common.views import LoginRequiredMixin
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .forms import CvrConfigurationForm, CprConfigurationForm, \
    GladdrregConfigurationForm
from .models import CvrConfig, CprConfig, GladdregConfig


class PluginConfigurationView(LoginRequiredMixin, UpdateView):

    plugin_name = None
    sectioned = False

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
        if self.sectioned:
            other = 'other'
            form = self.get_form()
            regex = re.compile('([a-zA-Z]+register)')
            sections = {}
            for (name, field) in form.fields.items():
                m = regex.match(name)
                key = other
                if m:
                    key = m.group(1)
                if not key in sections:
                    obj = {'items': []}
                    if key != other:
                        obj['name'] = key
                    sections[key] = obj
                sections[key]['items'].append(form[name])
            return ([sections[other]] if other in sections else []) + \
                   [values for key, values in sections.items() if key != other]
        else:
            return [{'items': self.get_form()}]


class CvrPluginConfigurationView(PluginConfigurationView):

    model = CvrConfig
    form_class = CvrConfigurationForm
    template_name = 'form.html'
    plugin_name = 'CVR'
    sectioned = True


class CprPluginConfigurationView(PluginConfigurationView):

    model = CprConfig
    form_class = CprConfigurationForm
    template_name = 'form.html'
    plugin_name = 'CPR'
    sectioned = True


class GladdregPluginConfigurationView(PluginConfigurationView):

    model = GladdregConfig
    form_class = GladdrregConfigurationForm
    template_name = 'form.html'
    plugin_name = 'Gladdrreg'


class PluginListTable(LoginRequiredMixin, TemplateView):

    template_name = 'table.html'

    def get_context_data(self, **kwargs):

        list = [
            {
                'name': 'CVR',
                'configlink': reverse('dafoconfig:plugin-cvr-edit'),
                'synclink': reverse('dafoconfig:plugin-pull', args=['cvr'])
            },
            {
                'name': 'CPR',
                'configlink': reverse('dafoconfig:plugin-cpr-edit'),
                'synclink': reverse('dafoconfig:plugin-pull', args=['cpr'])
            },
            {
                'name': 'Gladdrreg',
                'configlink': reverse('dafoconfig:plugin-gladdrreg-edit'),
                'synclink': reverse(
                    'dafoconfig:plugin-pull', args=['gladdrreg']
                )
            },
        ]

        order = self.request.GET.get('order', 'name')
        if order:
            reversed = False
            if order[0] == '-':
                order = order[1:]
                reversed = True
            if order == "name":
                list = sorted(
                    list, key=lambda item: item['name'],
                    reverse=reversed
                )


        context = {
            'list': list,
            'order': order
        }
        context.update(kwargs)
        return super(PluginListTable, self).get_context_data(**context)


class PluginListView(PluginListTable):

    template_name = 'list.html'


class PluginPullView(LoginRequiredMixin, TemplateView):

    template_name = 'pull.html'

    # def get_tokenheader(config, req):
    #     if req is None:
    #         username = config['username']
    #         password = config['password']
    #     else:
    #         username = req['username']
    #         password = req['password']
    #     tokenurl = config['tokenurl'] + \
    #                "?username=" + username + "&password=" + password
    #     token = requests.get(tokenurl).text
    #     return {'Authorization': 'SAML ' + token }

    status_conversion = {
        'cancelled': u'Afbrudt',
        'running': u'Kørende',
        'queued': u'Lagt i kø',
        'failure': u'Fejlet',
        'successful': u'Færdig'
    }

    def get_context_data(self, **kwargs):
        context = self.get_status()
        context.update(**kwargs)
        return context

    def get_plugin(self):
        return self.kwargs['plugin']

    def get_status(self):
        status = {}

        response = requests.get(
            "%s/command/pull/summary/all/running" % settings.PULLCOMMAND_HOST
        )
        if response.status_code == 200:
            running_pulls = response.json()
            for command in running_pulls:
                command['commandBody'] = json.loads(command['commandBody'])
            status['running'] = [
                {
                    'plugin': command['commandBody']['plugin'],
                    'id': command['id'],
                    'received': command.get('received')
                }
                for command in running_pulls
            ]

        response = requests.get(
            "%s/command/pull/summary/%s/latest" % (
                settings.PULLCOMMAND_HOST, self.get_plugin()
            )
        )
        if response.status_code == 200:
            latest_pulls = response.json()
            command = latest_pulls[0] if len(latest_pulls) > 0 else None
            print command
            if command is not None:
                command['commandBody'] = json.loads(command['commandBody'])
                status['latest'] = {
                    'plugin': command['commandBody']['plugin'],
                    'id': command['id'],
                    'received': command.get('received'),
                    'handled': command.get('handled'),
                    'status': self.status_conversion.get(
                        command.get('status')
                    ),
                    'errorMessage': command.get('errorMessage')
                }
        return status

    def post(self, request, *args, **kwargs):
        if request.POST.get('sync_start') is not None:
            requests.post(
                "%s/command/pull" % settings.PULLCOMMAND_HOST,
                json={'plugin': self.get_plugin()}
            )
        elif request.POST.get('sync_stop') is not None:
            id = request.POST.get('sync_stop')
            requests.delete("%s/command/%s" % (settings.PULLCOMMAND_HOST, id))
        return redirect(
            reverse('dafoconfig:plugin-pull', args=[self.get_plugin()])
        )
