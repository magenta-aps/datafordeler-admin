# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _


class SystemRole(object):
    TYPE_SERVICE = 1
    TYPE_ENTITY = 2
    TYPE_ATTRIBUTE = 3
    TYPE_CUSTOM = 4

    type_choices = (
        (TYPE_SERVICE, _(u"Servicerolle")),
        (TYPE_ENTITY, _(u"Entitetsrolle")),
        (TYPE_ATTRIBUTE, _(u"Attributrolle")),
        (TYPE_CUSTOM, _(u"Tilpasset rolletype")),
    )


class AccessAccount(object):

    STATUS_ACTIVE = 1
    STATUS_BLOCKED = 2
    STATUS_DEACTIVATED = 3

    status_choices = (
        (STATUS_ACTIVE, _(u"Aktiv")),
        (STATUS_BLOCKED, _(u"Blokeret")),
        (STATUS_DEACTIVATED, _(u"Deaktiveret")),
    )
