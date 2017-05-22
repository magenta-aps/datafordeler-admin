# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-22 13:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dafousers', '0006_more_fields_for_certificate_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificateuser',
            name='identification_mode',
            field=models.IntegerField(choices=[(1, 'Identificerer en enkelt bruger'), (2, "Identificerer brugere via 'p\xe5-vegne-af'")], default=1, verbose_name='Identifikationsmetode'),
        ),
        migrations.AddField(
            model_name='certificateuserhistory',
            name='identification_mode',
            field=models.IntegerField(choices=[(1, 'Identificerer en enkelt bruger'), (2, "Identificerer brugere via 'p\xe5-vegne-af'")], default=1, verbose_name='Identifikationsmetode'),
        ),
    ]
