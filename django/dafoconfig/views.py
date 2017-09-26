from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import UpdateView

from .models import CvrConfig
from .forms import CvrConfigurationForm


class ConfigurationView(UpdateView):

    def get_object(self, queryset=None):
        return self.model.objects.first()


class CvrConfigurationView(ConfigurationView):

    model = CvrConfig
    form_class = CvrConfigurationForm
    template_name = "form.html"
