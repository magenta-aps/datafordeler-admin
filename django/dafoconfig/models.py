# -*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

import django.db.models.options as options
import json
from django.db import models

if 'database' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('database',)


class CprConfig(models.Model):

    charset_choices = [
        (0, "US-ASCII"),
        (1, "ISO-8859-1"),
        (2, "UTF-8"),
        (3, "UTF-16BE"),
        (4, "UTF-16LE"),
        (5, "UTF-16")
    ]

    type_choices = [
        (-1, u"Deaktiveret"),
        (0, u"Lokal fil"),
        (1, u"FTP-server")
    ]

    id = models.CharField(primary_key=True, max_length=255)
    personregistertype = models.IntegerField(blank=True, null=True, verbose_name=u"Kildetype", choices=type_choices)
    personregisterdatacharset = models.IntegerField(blank=True, null=True, verbose_name=u"Forventet inputdata-tegnkodning", choices=charset_choices)
    personregisterftpaddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP adresse")
    personregisterftpusername = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP brugernavn")
    personregisterftppassword = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP password")
    personregisterlocalfile = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Lokal fil")
    personregisterpullcronschedule = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"CRON-tidsangivelse for automatisk hentning")

    residenceregistertype = models.IntegerField(blank=True, null=True, verbose_name=u"Kildetype", choices=type_choices)
    residenceregisterdatacharset = models.IntegerField(blank=True, null=True, verbose_name=u"Forventet inputdata-tegnkodning", choices=charset_choices)
    residenceregisterftpaddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP adresse")
    residenceregisterftpusername = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP brugernavn")
    residenceregisterftppassword = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP password")
    residenceregisterlocalfile = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Lokal fil")
    residenceregisterpullcronschedule = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"CRON-tidsangivelse for automatisk hentning")

    roadregistertype = models.IntegerField(blank=True, null=True, verbose_name=u"Kildetype", choices=type_choices)
    roadregisterdatacharset = models.IntegerField(blank=True, null=True, verbose_name=u"Forventet inputdata-tegnkodning", choices=charset_choices)
    roadregisterftpaddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP adresse")
    roadregisterftpusername = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP brugernavn")
    roadregisterftppassword = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP password")
    roadregisterlocalfile = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Lokal fil")
    roadregisterpullcronschedule = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"CRON-tidsangivelse for automatisk hentning")

    class Meta:
        managed = False
        database = 'configuration'
        db_table = 'cpr_config'


class CvrConfig(models.Model):

    type_choices = [
        (-1, u"Deaktiveret"),
        (1, u"HTTP-server")
    ]

    id = models.CharField(primary_key=True, max_length=255)
    registeraddress = models.CharField(max_length=255, blank=True, null=True)
    pullcronschedule = models.CharField(max_length=255, blank=True, null=True)


    companyregistertype = models.IntegerField(blank=True, null=True, verbose_name=u"Kildetype", choices=type_choices)
    companyregisterstartaddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Scan/scroll startadresse")
    companyregisterscrolladdress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Scan/scroll dataadresse")
    companyregisterusername = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Brugernavn")
    companyregisterpassword = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Password")
    companyregisterquery = models.CharField(max_length=1024, blank=True, null=True, verbose_name=u"Forespørgsel")

    companyunitregistertype = models.IntegerField(blank=True, null=True, verbose_name=u"Kildetype", choices=type_choices)
    companyunitregisterstartaddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Scan/scroll startadresse")
    companyunitregisterscrolladdress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Scan/scroll dataadresse")
    companyunitregisterusername = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Brugernavn")
    companyunitregisterpassword = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Password")
    companyunitregisterquery = models.CharField(max_length=1024, blank=True, null=True, verbose_name=u"Forespørgsel")

    participantregistertype = models.IntegerField(blank=True, null=True, verbose_name=u"Kildetype", choices=type_choices)
    participantregisterstartaddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Scan/scroll startadresse")
    participantregisterscrolladdress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Scan/scroll dataadresse")
    participantregisterusername = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Brugernavn")
    participantregisterpassword = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Password")
    participantregisterquery = models.CharField(max_length=1024, blank=True, null=True, verbose_name=u"Forespørgsel")


    class Meta:
        managed = False
        database = 'configuration'
        db_table = 'cvr_config'


class GladdregConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    pullcronschedule = models.CharField(max_length=255, blank=True, null=True)
    registeraddress = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        database = 'configuration'
        db_table = 'gladdreg_config'


class Command(models.Model):

    STATUS_QUEUED = 0
    STATUS_PROCESSING = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3
    STATUS_CANCEL = 4
    STATUS_CANCELLED = 5

    status_choices = [
        (STATUS_QUEUED, u"I kø"),
        (STATUS_PROCESSING, u"Kører"),
        (STATUS_SUCCESS, u"Færdig"),
        (STATUS_FAILED, u"Fejlet"),
        (STATUS_CANCEL, u"Afbryder"),
        (STATUS_CANCELLED, u"Afbrudt")
    ]

    id = models.BigAutoField(primary_key=True)
    commandbody = models.CharField(max_length=255, blank=True, null=True)
    commandname = models.CharField(max_length=255)
    errormessage = models.CharField(max_length=2048, blank=True, null=True)
    handled = models.DateTimeField(blank=True, null=True)
    issuer = models.CharField(max_length=255)
    received = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True, choices=status_choices)

    @property
    def commandbody_json(self):
        return json.loads(self.commandbody)

    class Meta:
        managed = False
        database = 'configuration'
        db_table = 'command'
