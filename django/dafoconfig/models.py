# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class CprConfig(models.Model):

    id = models.CharField(primary_key=True, max_length=255)
    personregisterdatacharset = models.IntegerField(blank=True, null=True, verbose_name=u"Forventet inputdata-tegnkodning")
    personregisterftpaddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP adresse")
    personregisterftppassword = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP password")
    personregisterftpusername = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"FTP brugernavn")
    personregisterlocalfile = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Lokal fil")
    personregisterpullcronschedule = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"CRON-tidsangivelse for automatisk hentning")
    personregistertype = models.IntegerField(blank=True, null=True, verbose_name=u"Kildetype")
    residenceregisterdatacharset = models.IntegerField(blank=True, null=True)
    residenceregisterftpaddress = models.CharField(max_length=255, blank=True, null=True)
    residenceregisterftppassword = models.CharField(max_length=255, blank=True, null=True)
    residenceregisterftpusername = models.CharField(max_length=255, blank=True, null=True)
    residenceregisterlocalfile = models.CharField(max_length=255, blank=True, null=True)
    residenceregisterpullcronschedule = models.CharField(max_length=255, blank=True, null=True)
    residenceregistertype = models.IntegerField(blank=True, null=True)
    roadregisterdatacharset = models.IntegerField(blank=True, null=True)
    roadregisterftpaddress = models.CharField(max_length=255, blank=True, null=True)
    roadregisterftppassword = models.CharField(max_length=255, blank=True, null=True)
    roadregisterftpusername = models.CharField(max_length=255, blank=True, null=True)
    roadregisterlocalfile = models.CharField(max_length=255, blank=True, null=True)
    roadregisterpullcronschedule = models.CharField(max_length=255, blank=True, null=True)
    roadregistertype = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        database = 'configuration'
        db_table = 'cpr_config'


class CvrConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    password = models.CharField(max_length=255, blank=True, null=True)
    pullcronschedule = models.CharField(max_length=255, blank=True, null=True)
    registeraddress = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)

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
