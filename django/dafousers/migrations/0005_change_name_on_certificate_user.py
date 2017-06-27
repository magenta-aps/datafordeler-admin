# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-04 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dafousers', '0004_fix_unique_constraints_in_history'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificateuser',
            name='Navn',
        ),
        migrations.RemoveField(
            model_name='certificateuserhistory',
            name='Navn',
        ),
        migrations.AddField(
            model_name='certificateuser',
            name='name',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Navn'),
        ),
        migrations.AddField(
            model_name='certificateuserhistory',
            name='name',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Navn'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='fingerprint',
            field=models.CharField(blank=True, default='', max_length=4000, null=True, verbose_name='Hex-encoded SHA256 fingerprint'),
        ),
    ]