from django.contrib import admin
from django.db import models as django_models
# from django import forms
import dafousers.models

EXCLUDE_MODELS = [
    dafousers.models.AccessAccount,
]
CUSTOM_ADMIN_CLASSES = {
    # Empty for now
}


class DefaultModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, *args, **kwargs):
        perms = super(DefaultModelAdmin, self).get_model_perms(*args, **kwargs)

        # try:
        #     request = args[0]
        # except ValueError:
        #     request = None

        # if(request):
        #     url_name = request.resolver_match.url_name
        #     if (url_name in ('index', 'app_list') and
        #         self.model.__name__[-7:] == "History"):
        #         return {}

        return perms


def register_models(models, namespace=None):
    models = models.__dict__.iteritems()

    for name, value in models:
        # Skip stuff that is not classes
        if not isinstance(value, type):
            continue

        # Skip stuff that is not models
        if not issubclass(value, django_models.Model):
            continue

        if value._meta.abstract:
            continue

        # Skip stuff that is not native to the booking.models module
        if namespace is not None and not value.__module__ == namespace:
            continue

        if value in EXCLUDE_MODELS:
            continue

        cls = CUSTOM_ADMIN_CLASSES.get(value, None)

        kwargs = {
            # "formfield_overrides": {
            #     django_models.ManyToManyField: {
            #         'widget': forms.CheckboxSelectMultiple
            #     },
            # }
        }
        if hasattr(value, "admin_register_kwargs"):
            kwargs.update(value.admin_register_kwargs())

        if cls is not None:
            admin.site.register(value, cls, **kwargs)
        else:
            admin.site.register(value, DefaultModelAdmin, **kwargs)


register_models(dafousers.models, 'dafousers.models')
