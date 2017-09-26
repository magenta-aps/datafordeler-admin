# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from OpenSSL import crypto, SSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from django.db import models
from django.conf import settings
from django.core.exceptions import FieldError
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile, File
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.urls import reverse
from dafousers import model_constants
from dafousers.dbfixes import fix_sql_server_schemas
from xml.etree import ElementTree

import base64
import copy
import hashlib
import jks
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
        new_class._meta.verbose_name_plural = "Historik for %s" % (
            entity_class._meta.verbose_name_plural
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

    def get_updated_user_profiles(self, user, submitted):
        editable_user_profiles = user.dafoauthinfo.admin_user_profiles

        other_user_profiles = self.user_profiles.all().exclude(
            pk__in=editable_user_profiles
        )

        return other_user_profiles.distinct() | submitted.distinct()


class PasswordUserQuerySet(models.QuerySet):
    def search(self, term):
        return self.filter(
            models.Q(givenname__contains=term) |
            models.Q(lastname__contains=term) |
            models.Q(email__contains=term)
        )


class PasswordUser(AccessAccount, EntityWithHistory):

    class Meta:
        # db_table = 'dbo].[dafousers_passworduser'
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
    # Have to use CharField for UUID since SQL Server and Django does not
    # agree on how to handle UUIDs.
    person_identification = models.CharField(
        verbose_name=_(u"Grunddata personidentifikation UUID"),
        max_length=40,
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

    def check_password(self, password):
        pwdata = hashlib.sha256()
        pwdata.update(password + self.password_salt)
        return base64.b64encode(pwdata.digest()) == self.encrypted_password

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

    def create_cert(self, years_valid):

        # load jks file
        keystore = jks.KeyStore.load(settings.ROOT_CERT, 'password')
        pk_entry = keystore.private_keys[settings.ROOT_CERT_ALIAS]
        private_key = crypto.load_privatekey(crypto.FILETYPE_ASN1, pk_entry.pkey)
        public_cert = crypto.load_certificate(crypto.FILETYPE_ASN1, pk_entry.cert_chain[0][1])

        # create cert req
        public_key = crypto.PKey()
        public_key.generate_key(crypto.TYPE_RSA, 2048)

        cert_req = crypto.X509Req()
        cert_req.get_subject().CN = self.contact_email
        cert_req.set_pubkey(public_key)
        cert_req.sign(private_key, b"sha256")

        # create a cert
        cert = crypto.X509()
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(years_valid*365*24*60*60)
        cert.set_issuer(public_cert.get_subject())
        cert.set_subject(cert_req.get_subject())
        cert.set_pubkey(cert_req.get_pubkey())
        cert.sign(private_key, b"sha256")

        p12 = crypto.PKCS12()
        p12.set_privatekey(cert_req.get_pubkey())
        p12.set_certificate(cert)

        certificate_name = "newcert-%s.crt" % os.getpid()
        return ContentFile(
            p12.export(),
            name=certificate_name,
        )

    def create_certificate(self, years_valid):
        certificate_file = self.create_cert(years_valid)
        obj = self.certificates.create(certificate_file=certificate_file)


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
            models.Q(name__contains=term)
        )


class IdentityProviderAccount(AccessAccount, EntityWithHistory):

    class Meta:
        verbose_name = _(u"organisation")
        verbose_name_plural = _(u"organisationer")

    objects = IdentityProviderAccountQuerySet.as_manager()
    CONSTANTS = model_constants.IdentityProviderAccount

    name = models.CharField(
        verbose_name=_(u"Navn"),
        max_length=2048,
        blank=True,
        default=""
    )
    idp_entity_id = models.CharField(
        verbose_name=_(u"EntityID"),
        max_length=2048,
        blank=True,
        default=""
    )
    idp_type = models.IntegerField(
        verbose_name=_(u"IdP type"),
        choices=CONSTANTS.idp_type_choices,
        default=CONSTANTS.IDP_TYPE_SECONDARY
    )
    metadata_xml_file = models.FileField(
        verbose_name=_(u"Metadata-xml-fil"),
        null=True,
        blank=True,
        upload_to="uploads",
    )
    metadata_xml = models.TextField(
        verbose_name=_(u"Metadata XML"),
        blank=True,
        default=""
    )
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
    organisation = models.TextField(
        verbose_name=_(u"Yderligere information om organisationen"),
        blank=True,
        default=""
    )

    userprofile_attribute = models.CharField(
        verbose_name=_(u"SAML-attribut der indeholder brugerprofiler"),
        max_length=2048,
        blank=True,
        default=""
    )

    userprofile_attribute_format = models.IntegerField(
        verbose_name=_(u"Format for brugerprofil attribut"),
        choices=CONSTANTS.userprofile_attribute_format_choices,
        default=CONSTANTS.USERPROFILE_FORMAT_MULTIVALUE,
    )

    userprofile_adjustment_filter_type = models.IntegerField(
        verbose_name=_(u"Tilpasninger til brugerprofil værdier"),
        choices=CONSTANTS.userprofile_filter_choices,
        default=CONSTANTS.USERPROFILE_FILTER_NONE
    )

    userprofile_adjustment_filter_value = models.CharField(
        verbose_name=_(u"Værdi brugt ved tilpasning af brugerprofiler"),
        max_length=2048,
        blank=True,
        default=""
    )

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse('dafousers:identityprovideraccount-list')

    def save(self, *args, **kwargs):
        result = super(IdentityProviderAccount, self).save(*args, **kwargs)

        if(self.metadata_xml_file and
                os.path.exists(self.metadata_xml_file.path)):

            try:
                # Store certificate in blob instead of file
                self.metadata_xml = self.metadata_xml_file.read()

                xml_root = ElementTree.fromstring(self.metadata_xml)
                self.idp_entity_id = xml_root.get("entityID")

                # Remove the file so data is only stored in the blob
                self.metadata_xml_file.close()
                self.metadata_xml_file.delete()
                self.metadata_xml_file = None

                # Save once more to store data retrieved from the uploaded file
                result = super(IdentityProviderAccount, self).save(
                    *args, **kwargs
                )
            except Exception as e:
                print "Failed to parse uploaded xml, error is: %s" % e

        # Update the last-update-of-idp-data timestamp
        UpdateTimestamps.touch(self.CONSTANTS.IDP_UPDATE_TIMESTAMP_NAME)

        return result

    @classmethod
    def get_readonly_fields(self):
        return ['metadata_xml', 'idp_entity_id']


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
        if self.certificate_file:
            try:
                # Store certificate in blob instead of file
                self.certificate_blob = self.certificate_file.read()
                p12 = crypto.load_pkcs12(self.certificate_blob)
                p12cert = p12.get_certificate()
                x509_cert = p12cert.to_cryptography()

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
                if os.path.exists(self.certificate_file.path):
                    self.certificate_file.close()
                    self.certificate_file.delete()

                self.certificate_file = None
            except Exception as e:
                print "Failed to parse certificate, error is: %s" % e

            # TODO: Update next expire date for all related objects.

        return result

    @classmethod
    def get_readonly_fields(self):
        return ['fingerprint', 'subject', 'valid_from', 'valid_to']

    def __unicode__(self):
        return unicode(
            self.valid_to.strftime("%Y-%m-%d %H:%M:%S") or
            _(u"Certifikat uden subjekt")
        )


class UserProfileQuerySet(models.QuerySet):
    def search(self, term):
        return self.filter(
            models.Q(name__contains=term)
        )


class UserProfile(EntityWithHistory):

    class Meta:
        verbose_name = _(u"brugerprofil")
        verbose_name_plural = _(u"brugerprofiler")

    objects = UserProfileQuerySet.as_manager()

    name = models.CharField(
        verbose_name=_(u"Navn"),
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

    def get_updated_system_roles(self, user, submitted):
        editable_system_roles = user.dafoauthinfo.admin_system_roles

        other_system_roles = self.system_roles.all().exclude(
            pk__in=editable_system_roles
        )

        return other_system_roles.distinct() | submitted.distinct()

    def get_updated_area_restrictions(self, user, submitted):
        editable_area_restrictions = user.dafoauthinfo.admin_area_restrictions

        other_area_restrictions = self.area_restrictions.all().exclude(
            pk__in=editable_area_restrictions
        )

        return other_area_restrictions.distinct() | submitted.distinct()

    def __unicode__(self):
        return unicode(self.name)


UserProfileHistory = HistoryForEntity.build_from_entity_class(UserProfile)


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

    @property
    def related_area_restrictions(self):
        if self.role_type != self.constants.TYPE_SERVICE:
            if self.parent is not None:
                return self.parent.related_area_restrictions
            else:
                return AreaRestriction.objects.none()
        return AreaRestriction.objects.filter(
            area_restriction_type__service_name__iexact=self.role_name
        )

    @property
    def service_name(self):
        if self.role_type == self.constants.TYPE_SERVICE:
            return self.target_name
        else:
            if self.parent is not None:
                return self.parent.service_name
            else:
                return "<unknown>"

    def __unicode__(self):
        return unicode(
            '%s (%s, %s)' % (
                self.role_name,
                self.get_role_type_display(),
                self.service_name.upper()
            )
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

    @property
    def service_name(self):
        if self.area_restriction_type is not None:
            return self.area_restriction_type.service_name
        else:
            return "<unknown>"

    def __unicode__(self):
        return unicode("%s (%s)") % (
            self.name,
            self.service_name.upper()
        )


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


class UpdateTimestamps(models.Model):

    class Meta:
        verbose_name = _(u"Tidsstempel for opdatering")
        verbose_name_plural = _(u"Tidsstempler for opdatering")

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
    updated = models.DateTimeField(
        verbose_name=_(u"Opdateret"),
        default=timezone.now
    )

    @classmethod
    def touch(cls, name):
        try:
            item = cls.objects.get(name=name)
        except UpdateTimestamps.DoesNotExist:
            item = cls(
                name=name,
                description=(_(u"Auto-genereret tidsstempel for %s") % name)
            )
        item.updated = timezone.now()
        item.save()


fix_sql_server_schemas()
