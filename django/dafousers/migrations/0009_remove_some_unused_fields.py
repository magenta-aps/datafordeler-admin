# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-18 12:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    replaces = [(b'dafousers', '0009_auto_20170918_1143'), (b'dafousers', '0010_auto_20170918_1429')]

    dependencies = [
        ('dafousers', '0008_updates_2017_09_15'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='userprofilehistory',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='identityprovideraccount',
            name='next_expiration',
        ),
        migrations.RemoveField(
            model_name='identityprovideraccounthistory',
            name='next_expiration',
        ),
    ]