# Generated by Django 2.2.6 on 2020-10-26 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20200706_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='abacpolicy',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='abacrule',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
