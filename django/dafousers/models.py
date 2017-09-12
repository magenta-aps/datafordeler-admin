# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from django.db import models
from django.conf import settings
from django.core.exceptions import FieldError
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.urls import reverse
from dafousers import model_constants

import base64
import copy
import hashlib
import os
import uuid


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
                    self._meta.get_field('changed_by').verbose_name
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
                "entity_class": entity_class,
                "hide_in_dafoadmin": True,
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
                seen_fields.add(f.name)

                # Skip one-to-one relations, usually used in inheritance
                if f.one_to_one:
                    continue

                new_field = copy.deepcopy(f)
                # Can not have unique fields in a history table
                new_field._unique = False
                new_class.add_to_class(f.name, new_field)

            for f in field_source._meta.local_many_to_many:
                if f.name in seen_fields:
                    continue
                seen_fields.add(f.name)

                new_class.add_to_class(f.name, models.ManyToManyField(
                    f.remote_field.model,
                    verbose_name=f.verbose_name,
                    blank=f.blank,
                ))

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

    class Meta:
        verbose_name = _(u"brugeridentifikation")
        verbose_name_plural = _(u"brugeridentifikationer")

    hide_in_dafoadmin = True

    user_id = models.CharField(
        verbose_name=_(u"Bruger identifikation (e-mail adresse)"),
        max_length=2048
    )

    def __unicode__(self):
        return unicode(self.user_id)


class AccessAccount(models.Model):

    constants = model_constants.AccessAccount

    identified_user = models.ForeignKey(
        UserIdentification,
        verbose_name=_(u"Identificerer bruger"),
        blank=True,
        null=True,
    )
    status = models.IntegerField(
        verbose_name=_(u"Status"),
        choices=constants.status_choices,
        default=constants.STATUS_ACTIVE
    )
    user_profiles = models.ManyToManyField(
        'UserProfile',
        verbose_name=_("Tilknyttede brugerprofiler"),
        blank=True
    )


class PasswordUserQuerySet(models.QuerySet):
    def search(self, term):
        return self.filter(
            models.Q(givenname__contains=term) | models.Q(lastname__contains=term)
        )


class PasswordUser(AccessAccount, EntityWithHistory):

    class Meta:
        verbose_name = _(u"bruger")
        verbose_name_plural = _(u"brugere")

    objects = PasswordUserQuerySet.as_manager()

    givenname = models.CharField(
        verbose_name=_(u"Fornavn"),
        max_length=2048,
        blank=True,
        default=""
    )
    lastname = models.CharField(
        verbose_name=_(u"Efternavn"),
        max_length=2048,
        blank=True,
        default=""
    )
    email = models.EmailField(
        verbose_name=_(u"E-mail"),
        unique=True,
        blank=False
    )
    organisation = models.CharField(
        verbose_name=_(u"Information om brugerens organisation"),
        max_length=2048,
        blank=True,
        default=""
    )
    encrypted_password = models.CharField(
        verbose_name=_(u"Krypteret password"),
        max_length=255,
        blank=True,
        default=""
    )
    password_salt = models.CharField(
        verbose_name=_(u"Password salt"),
        max_length=255,
        blank=True,
        default=""
    )
    person_identification = models.UUIDField(
        verbose_name=_(u"Grunddata personidentifikation UUID"),
        blank=True,
        null=True,
        default=uuid.uuid4
    )

    @staticmethod
    def generate_encrypted_password_and_salt(password):
        salt = base64.b64encode(os.urandom(16))
        pwdata = hashlib.sha256()
        pwdata.update(password + salt)
        return salt, base64.b64encode(pwdata.digest())

    def __unicode__(self):
        return '%s %s <%s>' % (self.givenname, self.lastname, self.email)


    def get_absolute_url(self):
        return reverse('dafousers:passworduser-list')


PasswordUserHistory = HistoryForEntity.build_from_entity_class(PasswordUser)


class EntityWithCertificate(models.Model):

    class Meta:
        abstract = True

    contact_name = models.CharField(
        verbose_name=_(u"Navn på kontaktperson"),
        max_length=2048,
        blank=True,
        default=""
    )
    contact_email = models.EmailField(
        verbose_name=_(u"E-mailadresse på kontaktperson"),
        blank=False
    )
    certificates = models.ManyToManyField(
        "Certificate",
        verbose_name=_(u"Certifikater")
    )

    @property
    def latest_certificate(self):
        return self.certificates.all().order_by("valid_to").first()


class CertificateUserQuerySet(models.QuerySet):
    def search(self, term):
        return self.filter(
            models.Q(name__contains=term)
        )


class CertificateUser(AccessAccount, EntityWithCertificate, EntityWithHistory):

    class Meta:
        verbose_name = _(u"system")
        verbose_name_plural = _(u"systemer")

    objects = CertificateUserQuerySet.as_manager()

    name = models.CharField(
        verbose_name=_(u"Navn"),
        max_length=2048,
        blank=True,
        default=""
    )
    identification_mode = models.IntegerField(
        verbose_name=_("Identifikationsmetode"),
        choices=model_constants.CertificateUser.mode_choices,
        default=model_constants.CertificateUser.MODE_IDENTIFIES_SINGLE_USER,
    )
    organisation = models.TextField(
        verbose_name=_(u"Information om brugerens organisation"),
        blank=True,
        default=""
    )
    comment = models.TextField(
        verbose_name=_(u"Kommentar/noter"),
        blank=True,
        default=""
    )

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse('dafousers:passworduser-list')


CertificateUserHistory = HistoryForEntity.build_from_entity_class(
    CertificateUser
)


class IdentityProviderAccountQuerySet(models.QuerySet):
    def search(self, term):
        return self.filter(
            models.Q(Navn__contains=term)
        )


class IdentityProviderAccount(AccessAccount, EntityWithCertificate,
                              EntityWithHistory):

    class Meta:
        verbose_name = _(u"organisation")
        verbose_name_plural = _(u"organisationer")

    objects = IdentityProviderAccountQuerySet.as_manager()

    name = models.CharField(
        name=_(u"Navn"),
        max_length=2048,
        blank=True,
        default=""
    )
    metadata_xml = models.TextField(
        verbose_name=_(u"Metadata XML"),
        blank=True,
        default=""
    )
    sso_endpoint = models.CharField(
        name=_(u"Single-Sign-On Endpoint"),
        max_length=2048,
        blank=True,
        default=""
    )
    slo_endpoint = models.CharField(
        name=_(u"Single-Log-Out Endpoint"),
        max_length=2048,
        blank=True,
        default=""
    )
    organisation = models.TextField(
        verbose_name=_(u"Information om brugerens organisation"),
        blank=True,
        default=""
    )
    nameid_format = models.CharField(
        name=_(u"NameID format"),
        max_length=2048,
        blank=True,
        default=""
    )

    def __unicode__(self):
        return unicode(self.Navn)


IdentityProviderAccountHistory = HistoryForEntity.build_from_entity_class(
    IdentityProviderAccount
)


class Certificate(models.Model):

    class Meta:
        verbose_name = _(u"certifikat")
        verbose_name_plural = _(u"certifikater")

    subject = models.CharField(
        verbose_name=_("Certifikat subjekt"),
        max_length=4000,
        blank=True,
        null=True,
        default=""
    )

    fingerprint = models.CharField(
        verbose_name=_(u"Hex-encoded SHA256 fingerprint"),
        # MSSQL max is 4000
        max_length=4000,
        blank=True,
        null=True,
        default=""
    )
    certificate_file = models.FileField(
        verbose_name=_(u"Certifikat-fil"),
        null=True,
        blank=True,
        upload_to="uploads",
    )
    certificate_blob = models.BinaryField(
        verbose_name=_(u"Certifikat (binære data)"),
        null=True,
        blank=True
    )
    valid_from = models.DateTimeField(
        verbose_name=_(u"Gyldig fra"),
        null=True,
        blank=True
    )
    valid_to = models.DateTimeField(
        verbose_name=_(u"Gyldig til"),
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['valid_to']

    def save(self, *args, **kwargs):
        # Save once, making sure files are written
        result = super(Certificate, self).save(*args, **kwargs)
        if(self.certificate_file and
           os.path.exists(self.certificate_file.path)):

            try:
                # Store certificate in blob instead of file
                self.certificate_blob = self.certificate_file.read()
                x509_cert = x509.load_pem_x509_certificate(
                    self.certificate_blob,
                    default_backend()
                )

                # Calculate and format sha256 fingerprint
                # (hex encoded bytes separated by ":")
                fingerprint_bytes = x509_cert.fingerprint(hashes.SHA256())
                self.fingerprint = ":".join(
                    "{:02x}".format(ord(c)) for c in fingerprint_bytes
                )

                # Store valid time interval
                self.valid_from = x509_cert.not_valid_before.replace(
                    tzinfo=timezone.UTC()
                )
                self.valid_to = x509_cert.not_valid_after.replace(
                    tzinfo=timezone.UTC()
                )

                subject_parts = []
                for (x, y) in (
                    ("C", NameOID.COUNTRY_NAME),
                    ("ST", NameOID.STATE_OR_PROVINCE_NAME),
                    ("L", NameOID.LOCALITY_NAME),
                    ("O", NameOID.ORGANIZATION_NAME),
                    ("OU", NameOID.ORGANIZATIONAL_UNIT_NAME),
                    ("CN", NameOID.COMMON_NAME),
                    ("emailAddress", NameOID.EMAIL_ADDRESS)
                ):
                    attrs = x509_cert.subject.get_attributes_for_oid(y)
                    if attrs and len(attrs) > 0:
                        subject_parts.append("%s=%s" % (x, attrs[0].value))

                self.subject = ", ".join(subject_parts)

                # Remove the file so data is only stored in the blob
                self.certificate_file.close()
                self.certificate_file.delete()
                self.certificate_file = None

                # Save once more to store data retrieved from the certificate
                result = super(Certificate, self).save(*args, **kwargs)
            except Exception as e:
                print "Failed to parse certificate, error is: %s" % e

            # TODO: Update next expire date for all related objects.

        return result

    @classmethod
    def get_readonly_fields(self):
        return ['fingerprint', 'subject', 'valid_from', 'valid_to']

    def __unicode__(self):
        return unicode(
            self.subject or
            _(u"Certifikat uden subjekt")
        )


class UserProfileQuerySet(models.QuerySet):
    def search(self, term):
        return self.filter(
            models.Q(name__contains=term)
        )


class UserProfile(models.Model):

    class Meta:
        verbose_name = _(u"brugerprofil")
        verbose_name_plural = _(u"brugerprofiler")

    objects = UserProfileQuerySet.as_manager()

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
    area_restrictions = models.ManyToManyField(
        'AreaRestriction',
        verbose_name=_("Tilknyttede områdebegrænsninger"),
        blank=True
    )

    def __unicode__(self):
        return unicode(self.name)


class SystemRole(models.Model):

    class Meta:
        verbose_name = _(u"systemrolle")
        verbose_name_plural = _(u"systemroller")

    hide_in_dafoadmin = True

    constants = model_constants.SystemRole

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
        choices=constants.type_choices,
        default=constants.TYPE_CUSTOM
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


class AreaRestriction(models.Model):

    class Meta:
        verbose_name = _(u"områdeafgrænsning")
        verbose_name_plural = _(u"områdeafgrænsninger")

    hide_in_dafoadmin = True

    name = models.CharField(
        verbose_name=_(u"Navn"),
        max_length=2048
    )
    description = models.TextField(
        verbose_name=_(u"Beskrivelse"),
        blank=True,
        default=""
    )
    sumiffiik = models.UUIDField(
        verbose_name=_(u"Sumiffiik"),
        blank=True,
        null=True,
        default=""
    )
    area_restriction_type = models.ForeignKey(
        "AreaRestrictionType",
        verbose_name=_(u"Type"),
        blank=False,
        null=False,
    )

    def __unicode__(self):
        return unicode(self.name)


class AreaRestrictionType(models.Model):

    class Meta:
        verbose_name = _(u"områdeafgrænsningstype")
        verbose_name_plural = _(u"områdeafgrænsningstyper")

    hide_in_dafoadmin = True

    name = models.CharField(
        verbose_name=_(u"Navn"),
        max_length=2048
    )
    description = models.TextField(
        verbose_name=_(u"Beskrivelse"),
        blank=True,
        default=""
    )
    service_name = models.CharField(
        verbose_name=_(u"Navn på associeret service"),
        max_length=2048
    )

    def __unicode__(self):
        return unicode(self.name)
