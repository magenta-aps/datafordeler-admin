# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-04 14:07
from __future__ import unicode_literals

import uuid

import dafousers.models
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Aktiv'), (2, 'Blokeret'), (3, 'Deaktiveret')], default=1, verbose_name='Status')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PasswordUserHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_by', models.CharField(max_length=2048, verbose_name='\xc6ndret af')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Seneste opdatering')),
                ('status', models.IntegerField(choices=[(1, 'Aktiv'), (2, 'Blokeret'), (3, 'Deaktiveret')], default=1, verbose_name='Status')),
                ('fullname', models.CharField(blank=True, default='', max_length=2048, verbose_name='Fulde navn')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('organisation', models.TextField(blank=True, default='', verbose_name='Information om brugerens organisation')),
                ('encrypted_password', models.CharField(blank=True, default='', max_length=4000, verbose_name='Krypteret password')),
                ('person_identification', models.CharField(blank=True, default=uuid.uuid4, max_length=40, null=True, verbose_name='Grunddata personidentifikation UUID')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, dafousers.models.HistoryForEntity),
        ),
        migrations.CreateModel(
            name='SystemRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=2048, verbose_name='Navn')),
                ('role_type', models.IntegerField(choices=[(1, 'Servicerolle'), (2, 'Entitetsrolle'), (3, 'Attributrolle'), (4, 'Tilpasset rolletype')], default=4, verbose_name='Type')),
                ('target_name', models.CharField(blank=True, max_length=2048, verbose_name='Objekt rollen giver adgang til')),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='dafousers.SystemRole', verbose_name='For\xe6ldre-rolle')),
            ],
        ),
        migrations.CreateModel(
            name='UserIdentification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=2048, verbose_name='Bruger identifikation (e-mail adresse)')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2048, verbose_name='Navn')),
                ('created_by', models.CharField(max_length=2048, verbose_name='Oprettet af')),
                ('system_roles', models.ManyToManyField(blank=True, to='dafousers.SystemRole', verbose_name='Tilknyttede systemroller')),
            ],
        ),
        migrations.CreateModel(
            name='PasswordUser',
            fields=[
                ('accessaccount_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dafousers.AccessAccount')),
                ('changed_by', models.CharField(max_length=2048, verbose_name='\xc6ndret af')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Opdateret')),
                ('fullname', models.CharField(blank=True, default='', max_length=2048, verbose_name='Fulde navn')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('organisation', models.TextField(blank=True, default='', verbose_name='Information om brugerens organisation')),
                ('encrypted_password', models.CharField(blank=True, default='', max_length=4000, verbose_name='Krypteret password')),
                ('person_identification', models.CharField(blank=True, default=uuid.uuid4, max_length=40, null=True, verbose_name='Grunddata personidentifikation UUID')),
            ],
            options={
                'abstract': False,
            },
            bases=('dafousers.accessaccount', models.Model),
        ),
        migrations.AddField(
            model_name='passworduserhistory',
            name='identified_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dafousers.UserIdentification', verbose_name='Identificerer bruger'),
        ),
        migrations.AddField(
            model_name='passworduserhistory',
            name='user_profiles',
            field=models.ManyToManyField(blank=True, to='dafousers.UserProfile', verbose_name='Tilknyttede brugerprofiler'),
        ),
        migrations.AddField(
            model_name='accessaccount',
            name='identified_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dafousers.UserIdentification', verbose_name='Identificerer bruger'),
        ),
        migrations.AddField(
            model_name='accessaccount',
            name='user_profiles',
            field=models.ManyToManyField(blank=True, to='dafousers.UserProfile', verbose_name='Tilknyttede brugerprofiler'),
        ),
        migrations.AddField(
            model_name='passworduserhistory',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dafousers.PasswordUser'),
        ),
        migrations.AlterField(
            model_name='passworduserhistory',
            name='updated',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Opdateret'),
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('figerprint', models.CharField(blank=True, default='', max_length=4000, null=True)),
                ('certificate_blob', models.BinaryField(verbose_name='Certifikat (bin\xe6re data)')),
                ('valid_from', models.DateTimeField(verbose_name='Gyldig fra')),
                ('valid_to', models.DateTimeField(verbose_name='Gyldig til')),
            ],
        ),
        migrations.CreateModel(
            name='CertificateUser',
            fields=[
                ('accessaccount_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dafousers.AccessAccount')),
                ('changed_by', models.CharField(max_length=2048, verbose_name='\xc6ndret af')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Opdateret')),
                ('contact_name', models.CharField(blank=True, default='', max_length=2048, verbose_name='Navn p\xe5 kontaktperson')),
                ('contact_email', models.EmailField(max_length=254, verbose_name='E-mailadresse p\xe5 kontaktperson')),
                ('next_expiration', models.DateTimeField(blank=True, default=None, null=True, verbose_name='N\xe6ste udl\xf8bsdato for certifikat(er)')),
                ('Navn', models.CharField(blank=True, default='', max_length=2048)),
                ('organisation', models.TextField(blank=True, default='', verbose_name='Information om brugerens organisation')),
                ('comment', models.TextField(blank=True, default='', verbose_name='Kommentar/noter')),
                ('certificates', models.ManyToManyField(to='dafousers.Certificate', verbose_name='Certifikater')),
            ],
            options={
                'abstract': False,
            },
            bases=('dafousers.accessaccount', models.Model),
        ),
        migrations.CreateModel(
            name='CertificateUserHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_by', models.CharField(max_length=2048, verbose_name='\xc6ndret af')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Opdateret')),
                ('status', models.IntegerField(choices=[(1, 'Aktiv'), (2, 'Blokeret'), (3, 'Deaktiveret')], default=1, verbose_name='Status')),
                ('contact_name', models.CharField(blank=True, default='', max_length=2048, verbose_name='Navn p\xe5 kontaktperson')),
                ('contact_email', models.EmailField(max_length=254, verbose_name='E-mailadresse p\xe5 kontaktperson')),
                ('next_expiration', models.DateTimeField(blank=True, default=None, null=True, verbose_name='N\xe6ste udl\xf8bsdato for certifikat(er)')),
                ('Navn', models.CharField(blank=True, default='', max_length=2048)),
                ('organisation', models.TextField(blank=True, default='', verbose_name='Information om brugerens organisation')),
                ('comment', models.TextField(blank=True, default='', verbose_name='Kommentar/noter')),
                ('certificates', models.ManyToManyField(to='dafousers.Certificate', verbose_name='Certifikater')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dafousers.CertificateUser')),
                ('identified_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dafousers.UserIdentification', verbose_name='Identificerer bruger')),
                ('user_profiles', models.ManyToManyField(blank=True, to='dafousers.UserProfile', verbose_name='Tilknyttede brugerprofiler')),
            ],
            bases=(models.Model, dafousers.models.HistoryForEntity),
        ),
        migrations.CreateModel(
            name='IdentityProviderAccount',
            fields=[
                ('accessaccount_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dafousers.AccessAccount')),
                ('changed_by', models.CharField(max_length=2048, verbose_name='\xc6ndret af')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Opdateret')),
                ('contact_name', models.CharField(blank=True, default='', max_length=2048, verbose_name='Navn p\xe5 kontaktperson')),
                ('contact_email', models.EmailField(max_length=254, verbose_name='E-mailadresse p\xe5 kontaktperson')),
                ('next_expiration', models.DateTimeField(blank=True, default=None, null=True, verbose_name='N\xe6ste udl\xf8bsdato for certifikat(er)')),
                ('metadata_xml', models.TextField(blank=True, default='', verbose_name='Metadata XML')),
                ('Single-Sign-On Endpoint', models.CharField(blank=True, default='', max_length=2048)),
                ('Single-Log-Out Endpoint', models.CharField(blank=True, default='', max_length=2048)),
                ('organisation', models.TextField(blank=True, default='', verbose_name='Information om brugerens organisation')),
                ('NameID format', models.CharField(blank=True, default='', max_length=2048)),
                ('certificates', models.ManyToManyField(to='dafousers.Certificate', verbose_name='Certifikater')),
            ],
            options={
                'abstract': False,
            },
            bases=('dafousers.accessaccount', models.Model),
        ),
        migrations.CreateModel(
            name='IdentityProviderAccountHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_by', models.CharField(max_length=2048, verbose_name='\xc6ndret af')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Opdateret')),
                ('status', models.IntegerField(choices=[(1, 'Aktiv'), (2, 'Blokeret'), (3, 'Deaktiveret')], default=1, verbose_name='Status')),
                ('contact_name', models.CharField(blank=True, default='', max_length=2048, verbose_name='Navn p\xe5 kontaktperson')),
                ('contact_email', models.EmailField(max_length=254, verbose_name='E-mailadresse p\xe5 kontaktperson')),
                ('next_expiration', models.DateTimeField(blank=True, default=None, null=True, verbose_name='N\xe6ste udl\xf8bsdato for certifikat(er)')),
                ('metadata_xml', models.TextField(blank=True, default='', verbose_name='Metadata XML')),
                ('Single-Sign-On Endpoint', models.CharField(blank=True, default='', max_length=2048)),
                ('Single-Log-Out Endpoint', models.CharField(blank=True, default='', max_length=2048)),
                ('organisation', models.TextField(blank=True, default='', verbose_name='Information om brugerens organisation')),
                ('NameID format', models.CharField(blank=True, default='', max_length=2048)),
                ('certificates', models.ManyToManyField(to='dafousers.Certificate', verbose_name='Certifikater')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dafousers.IdentityProviderAccount')),
                ('identified_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dafousers.UserIdentification', verbose_name='Identificerer bruger')),
                ('user_profiles', models.ManyToManyField(blank=True, to='dafousers.UserProfile', verbose_name='Tilknyttede brugerprofiler')),
                ('Navn', models.CharField(blank=True, default='', max_length=2048)),
            ],
            bases=(models.Model, dafousers.models.HistoryForEntity),
        ),
        migrations.CreateModel(
            name='AreaRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2048, verbose_name='Navn')),
                ('description', models.TextField(blank=True, default='', verbose_name='Beskrivelse')),
                ('sumiffiik', models.UUIDField(blank=True, default='', null=True, verbose_name='Sumiffiik')),
            ],
        ),
        migrations.CreateModel(
            name='AreaRestrictionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2048, verbose_name='Navn')),
                ('description', models.TextField(blank=True, default='', verbose_name='Beskrivelse')),
                ('service_name', models.CharField(max_length=2048, verbose_name='Navn p\xe5 associeret service')),
            ],
        ),
        migrations.AddField(
            model_name='arearestriction',
            name='area_restriction_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dafousers.AreaRestrictionType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='area_restrictions',
            field=models.ManyToManyField(blank=True, to='dafousers.AreaRestriction', verbose_name='Tilknyttede omr\xe5debegr\xe6nsninger'),
        ),
        migrations.AlterModelOptions(
            name='arearestriction',
            options={'verbose_name': 'omr\xe5deafgr\xe6nsning', 'verbose_name_plural': 'omr\xe5deafgr\xe6nsninger'},
        ),
        migrations.AlterModelOptions(
            name='arearestrictiontype',
            options={'verbose_name': 'omr\xe5deafgr\xe6nsningstype', 'verbose_name_plural': 'omr\xe5deafgr\xe6nsningstyper'},
        ),
        migrations.AlterModelOptions(
            name='certificate',
            options={'verbose_name': 'Certifikat', 'verbose_name_plural': 'Certifikater'},
        ),
        migrations.AlterModelOptions(
            name='certificateuser',
            options={'verbose_name': 'system', 'verbose_name_plural': 'systemer'},
        ),
        migrations.AlterModelOptions(
            name='identityprovideraccount',
            options={'verbose_name': 'Organisation', 'verbose_name_plural': 'Organisationer'},
        ),
        migrations.AlterModelOptions(
            name='passworduser',
            options={'verbose_name': 'bruger', 'verbose_name_plural': 'brugere'},
        ),
        migrations.AlterModelOptions(
            name='systemrole',
            options={'verbose_name': 'systemrolle', 'verbose_name_plural': 'systemroller'},
        ),
        migrations.AlterModelOptions(
            name='useridentification',
            options={'verbose_name': 'brugeridentifikation', 'verbose_name_plural': 'brugeridentifikationer'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'brugerprofil', 'verbose_name_plural': 'brugerprofiler'},
        ),
        migrations.RenameField(
            model_name='certificate',
            old_name='figerprint',
            new_name='fingerprint',
        ),
        migrations.AddField(
            model_name='identityprovideraccount',
            name='Navn',
            field=models.CharField(blank=True, default='', max_length=2048),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='certificate_blob',
            field=models.FileField(upload_to='get ', verbose_name='Certifikat (bin\xe6re data)'),
        ),
        migrations.AlterModelOptions(
            name='certificate',
            options={'verbose_name': 'certifikat', 'verbose_name_plural': 'certifikater'},
        ),
        migrations.AlterModelOptions(
            name='identityprovideraccount',
            options={'verbose_name': 'organisation', 'verbose_name_plural': 'organisationer'},
        ),
        migrations.AddField(
            model_name='passworduser',
            name='password_salt',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Password salt'),
        ),
        migrations.AddField(
            model_name='passworduserhistory',
            name='password_salt',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Password salt'),
        ),
        migrations.AlterField(
            model_name='passworduser',
            name='encrypted_password',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Krypteret password'),
        ),
        migrations.AlterField(
            model_name='passworduser',
            name='organisation',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Information om brugerens organisation'),
        ),
        migrations.AlterField(
            model_name='passworduserhistory',
            name='encrypted_password',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Krypteret password'),
        ),
        migrations.AlterField(
            model_name='passworduserhistory',
            name='organisation',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Information om brugerens organisation'),
        ),
        migrations.RemoveField(
            model_name='passworduser',
            name='fullname',
        ),
        migrations.RemoveField(
            model_name='passworduserhistory',
            name='fullname',
        ),
        migrations.AddField(
            model_name='passworduser',
            name='givenname',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Fornavn'),
        ),
        migrations.AddField(
            model_name='passworduser',
            name='lastname',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Efternavn'),
        ),
        migrations.AddField(
            model_name='passworduserhistory',
            name='givenname',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Fornavn'),
        ),
        migrations.AddField(
            model_name='passworduserhistory',
            name='lastname',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Efternavn'),
        ),
        migrations.AlterField(
            model_name='passworduser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='passworduserhistory',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='E-mail'),
        ),
    ]
