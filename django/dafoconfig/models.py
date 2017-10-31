# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

import django.db.models.options as options

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
    id = models.CharField(primary_key=True, max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    registeraddress = models.CharField(max_length=255, blank=True, null=True)
    pullcronschedule = models.CharField(max_length=255, blank=True, null=True)

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
