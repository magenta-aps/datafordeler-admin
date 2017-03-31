from django.contrib import admin
from django.db import models as django_models
import dafousers.models

EXCLUDE_MODELS = [
    dafousers.models.AccessAccount,
]
CUSTOM_ADMIN_CLASSES = {
    # Empty for now
}


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
        if cls is not None:
            admin.site.register(value, cls)
        else:
            admin.site.register(value)

register_models(dafousers.models, 'dafousers.models')
