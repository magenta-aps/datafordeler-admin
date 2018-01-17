# -*- coding: utf-8 -*-
import logging

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out


@receiver(user_logged_in)
def on_login(sender, signal, request, user):
    logging.getLogger('django.server').info(
        "User %s logged in", unicode(user)
    )

@receiver(user_logged_out)
def on_logout(sender, signal, request, user):
    logging.getLogger('django.server').info(
        "User %s logged out", unicode(user)
    )
