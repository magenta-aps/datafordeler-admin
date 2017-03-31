# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import apps
from django.db import models
from django.utils import formats
from django.utils import timezone
from django.utils.translation import ugettext as _

import copy


class EntityWithHistory(models.Model):

    class Meta:
        abstract = True

    history_class = None

    changed_by = models.CharField(
        verbose_name=_(u"Ændret af"),
        max_length=2048
    )
    updated = models.DateTimeField(
        verbose_name=_(u"Opdateret"),
        default=timezone.now
    )


    def save(self, *args, **kwargs):
        # Complain if changed_by has not been set
        if not self.changed_by:
            raise FieldError(
                '%s skal udfyldes ved hver opdatering' % (
                    EntityWithHistory.changed_by.verbose_name
                )
            )

        # Set latest update time to now
        self.updated = timezone.now()

        # Save ourselves
        result = super(EntityWithHistory, self).save(*args, **kwargs)

        # Save history record
        self.history_class.create_from_entity(self)

        return result


class HistoryForEntity(object):

    @classmethod
    def get_history_data_dict(cls, entity):
        data = {}
        data["_relations"] = {}

        own_fields = set([f.name for f in cls._meta.get_fields()])

        for f in entity.__class__._meta.get_fields():
            if f.name not in own_fields:
                continue

            value = getattr(entity, f.name, None)

            # If whatever we get has an all method, call that to retrieve
            # the actual values
            if callable(getattr(value, 'all', None)):
                data["_relations"][f.name] = value.all()
            else:
                data[f.name] = value

        del data['id']

        return data

    @classmethod
    def create_from_entity(cls, entity):
        data = cls.get_history_data_dict(entity)
        rel_data = data["_relations"]

        del data["_relations"]

        new_obj = cls(entity=entity, **data)
        new_obj.save()

        # Add many-to-many relation
        for r in rel_data:
            for v in rel_data[r]:
                getattr(new_obj, r).add(v.pk)

        return new_obj

    @classmethod
    def build_from_entity_class(cls, entity_class, *extra_parents):

        if EntityWithHistory not in entity_class.__bases__:
            raise ImproperlyConfigured(
                "Can not build %s from a class that does not " +
                "inherit from %s" % (
                    cls.__name__,
                    EntityWithHistory.__name__
                )
            )


        # Construct model class which inherits from cls and has an
        # entity field as a foreign key to the entity class.
        new_class = type(
            str(entity_class.__name__ + "History"),
            (models.Model, cls) + extra_parents,
            {
                "__module__": entity_class.__module__,
                "entity": models.ForeignKey(entity_class),
                "entity_class": entity_class
            }
        )
        
        entity_class.history_class = new_class

        # Copy fields from the entity class and its parents
        field_sources = [entity_class]
        field_sources.extend(reversed(entity_class.__bases__))



        seen_fields = set(["id", "entity"])
        
        for field_source in field_sources:
            if not issubclass(field_source, models.Model):
                continue

            for f in field_source._meta.local_fields:
                if f.name in seen_fields:
                    continue

                # Skip one-to-one relations, usually used in inheritance
                if f.one_to_one:
                    continue

                new_field = copy.deepcopy(f)
                new_class.add_to_class(f.name, new_field)
                seen_fields.add(f.name)
        
            for f in field_source._meta.local_many_to_many:
                if f.name in seen_fields:
                    continue

                new_field = models.ManyToManyField(
                    f.remote_field.model,
                    verbose_name=f.verbose_name,
                    blank=f.blank
                )
                new_class.add_to_class(f.name, new_field)
        
        new_class._meta.verbose_name = "Historik for %s" % (
            entity_class._meta.verbose_name
        )
        
        return new_class


    @classmethod
    def admin_register_kwargs(cls):
        return {"list_display": ['__unicode__', 'updated', 'changed_by']}

    def __unicode__(self):
        entity_unicode_method = self.entity_class.__unicode__.__func__

        return entity_unicode_method(self)


class UserIdentification(models.Model):
    user_id = models.CharField(
        verbose_name=_(u"Bruger identifikation (e-mail adresse)"),
        max_length=2048
    )

    def __unicode__(self):
        return unicode(self.user_id)

class AccessAccount(models.Model):

    STATUS_ACTIVE = 1
    STATUS_BLOCKED = 2
    STATUS_DEACTIVATED = 3

    status_choices = (
        (STATUS_ACTIVE, _(u"Aktiv")),
        (STATUS_BLOCKED, _(u"Blokeret")),
        (STATUS_DEACTIVATED, _(u"Deaktiveret")),
    )

    identified_user = models.ForeignKey(
        UserIdentification,
        verbose_name=_(u"Identificerer bruger"),
        blank=True,
        null=True,
    )
    status = models.IntegerField(
        verbose_name=_(u"Status"),
        choices=status_choices,
        default=STATUS_ACTIVE
    )
    user_profiles = models.ManyToManyField(
        'UserProfile',
        verbose_name=_("Tilknyttede brugerprofiler"),
        blank=True
    )


class PasswordUserFields(models.Model):
    class Meta:
        abstract = True

    fullname = models.CharField(
        verbose_name=_(u"Fulde navn"),
        max_length=2048,
        blank=True,
        default=""
    )
    email = models.EmailField(
        verbose_name=_(u"E-mail"),
        blank=False
    )
    organisation = models.TextField(
        verbose_name=_(u"Information om brugerens organisation"),
        blank=True,
        default=""
    )
    encrypted_password = models.CharField(
        verbose_name=_(u"Krypteret password"),
        max_length=4096,
        blank=True,
        default=""
    )
    person_identification = models.UUIDField(
        verbose_name=_(u"Grunddata personidentifikation UUID"),
        blank=True,
        null=True,
        default=""
    )


class PasswordUser(AccessAccount, PasswordUserFields, EntityWithHistory):

    def __unicode__(self):
        return '%s <%s>' % (self.fullname, self.email)

PasswordUserHistory = HistoryForEntity.build_from_entity_class(PasswordUser,)


class UserProfile(models.Model):
    name = models.CharField(
        verbose_name=_(u"Navn"),
        max_length=2048
    )
    created_by = models.CharField(
        verbose_name=_(u"Oprettet af"),
        max_length=2048
    )
    system_roles = models.ManyToManyField(
        'SystemRole',
        verbose_name=_("Tilknyttede systemroller"),
        blank=True
    )

    def __unicode__(self):
        return unicode(self.name)


class SystemRole(models.Model):

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

    parent = models.ForeignKey(
        'SystemRole',
        verbose_name=_(u"Forældre-rolle"),
        blank=True,
        null=True,
        default=None
    )
    role_name = models.CharField(
        verbose_name=_(u"Navn"),
        max_length=2048
    )
    role_type = models.IntegerField(
        verbose_name=_(u"Type"),
        choices=type_choices,
        default=TYPE_CUSTOM
    )
    target_name = models.CharField(
        verbose_name=_(u"Objekt rollen giver adgang til"),
        max_length=2048,
        blank=True
    )

    def __unicode__(self):
        return unicode(
            '%s (%s)' % (self.role_name, self.get_role_type_display())
        )
