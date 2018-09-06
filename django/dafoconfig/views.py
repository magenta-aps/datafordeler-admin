# -*- coding: utf-8 -*-

import json
import re

from common.views import LoginRequiredMixin
from datetime import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .forms import CvrConfigurationForm, CprConfigurationForm
from .forms import DumpConfigurationForm
from .forms import GladdrregConfigurationForm
from .models import CvrConfig, CprConfig, GeoConfig, GladdregConfig, Command
from .models import DumpConfig

logger = logging.getLogger('django.server')


class PluginConfigurationView(LoginRequiredMixin, UpdateView):

    plugin_name = None
    sectioned = False

    def get_object(self, queryset=None):
        return self.model.objects.first()

    def get_success_url(self):
        return reverse('dafoconfig:plugin-list')

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


class GeoPluginConfigurationView(PluginConfigurationView):

    model = GeoConfig
    form_class = CprConfigurationForm
    template_name = 'form.html'
    plugin_name = 'GEO'
    sectioned = True



class GladdregPluginConfigurationView(PluginConfigurationView):

    model = GladdregConfig
    form_class = GladdrregConfigurationForm
    template_name = 'form.html'
    plugin_name = 'Gladdrreg'


class PluginListTable(LoginRequiredMixin, TemplateView):

    template_name = 'table.html'

    def get_context_data(self, **kwargs):

        plugin_list = [
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
                'name': 'GEO',
                'configlink': reverse('dafoconfig:plugin-geo-edit'),
                'synclink': reverse('dafoconfig:plugin-pull', args=['geo'])
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
            do_reverse = False
            if order[0] == '-':
                order = order[1:]
                do_reverse = True
            if order == "name":
                plugin_list = sorted(
                    plugin_list, key=lambda item: item['name'],
                    reverse=do_reverse
                )

        context = {
            'list': plugin_list,
            'order': order
        }
        context.update(kwargs)
        return super(PluginListTable, self).get_context_data(**context)


class PluginListView(PluginListTable):

    template_name = 'list.html'


class PluginPullView(LoginRequiredMixin, TemplateView):

    template_name = 'pull.html'

    status_conversion = {
        Command.STATUS_CANCELLED: u'Afbrudt',
        Command.STATUS_PROCESSING: u'Kørende',
        Command.STATUS_QUEUED: u'Lagt i kø',
        Command.STATUS_FAILED: u'Fejlet',
        Command.STATUS_CANCEL: u'Afbryder',
        Command.STATUS_SUCCESS: u'Færdig'
    }

    available_command_names = [
        'pull'
    ]

    def get_context_data(self, **kwargs):
        context = self.get_status()
        context.update(**kwargs)
        return context

    def get_plugin(self):
        return self.kwargs['plugin']

    def get_status(self):
        status = {}

        running_pulls = self.get_pull_summary('all', 'running')
        status['running'] = [
            {
                'plugin': command.commandbody_json['plugin'],
                'id': command.id,
                'received': command.received
            }
            for command in running_pulls
        ]

        latest_pulls = self.get_pull_summary(self.get_plugin(), 'latest')
        command = latest_pulls[0] if len(latest_pulls) > 0 else None
        if command is not None:
            print command.status
            status['latest'] = {
                'plugin': command.commandbody_json['plugin'],
                'id': command.id,
                'received': command.received,
                'handled': command.handled,
                'status': self.status_conversion.get(
                    command.status
                ),
                'errorMessage': command.errormessage
            }

        return status

    def post(self, request, *args, **kwargs):
        if request.POST.get('sync_start') is not None:
            self.create_command('pull', {'plugin': self.get_plugin()})

        elif request.POST.get('sync_stop') is not None:
            id = request.POST.get('sync_stop')
            self.cancel_command(id)

        return redirect(
            reverse('dafoconfig:plugin-pull', args=[self.get_plugin()])
        )

    def create_command(self, command_name, command_data):
        if command_name in self.available_command_names:
            command = Command(
                commandname=command_name.lower(),
                commandbody=json.dumps(command_data),
                issuer="admin interface",
                received=datetime.now(),
                status=Command.STATUS_QUEUED
            )
            command.save()

    def cancel_command(self, command_id):
        try:
            command = Command.objects.get(id=command_id)
            command.status = Command.STATUS_CANCEL
            command.save()
        except Command.DoesNotExist:
            pass

    def get_pull_summary(self, plugin_name, state):
        commands = []
        valid_states = ['latest', 'running']
        if state not in valid_states:
            return []
        qs = Command.objects.filter(commandname='pull')
        if state == 'running':
            qs = qs.filter(
                status__in=[Command.STATUS_QUEUED, Command.STATUS_PROCESSING]
            )
        plugins = [plugin_name] \
            if plugin_name != 'all' \
            else ['cpr', 'cvr', 'gladdrreg']
        for plugin in plugins:
            pqs = qs.filter(
                commandbody__icontains="\"plugin\": \"%s\"" % plugin
            ).order_by('-handled')
            command = pqs.first()
            if command is not None:
                commands.append(command)
        return commands
