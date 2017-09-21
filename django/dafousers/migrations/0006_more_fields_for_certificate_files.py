# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-04 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dafousers', '0005_change_name_on_certificate_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='certificate_file',
            field=models.FileField(blank=True, null=True, upload_to='uploads', verbose_name='Certifikat-fil'),
        ),
        migrations.RemoveField(
            model_name='certificate',
            name='certificate_blob',
        ),
        migrations.AddField(
            model_name='certificate',
            name='certificate_blob',
            field=models.BinaryField(blank=True, null=True, verbose_name='Certifikat (bin\xe6re data)'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='subject',
            field=models.CharField(blank=True, default='', max_length=4000, null=True, verbose_name='Certifikat subjekt'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='valid_from',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Gyldig fra'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='valid_to',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Gyldig til'),
        ),
    ]
