# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-08-30 09:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('two_factor_auth', '0003_auto_20180830_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='secondauthfactor',
            name='type',
            field=models.CharField(choices=[('PHONE', 'Phone')], max_length=255),
        ),
    ]