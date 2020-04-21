# Generated by Django 2.2.6 on 2020-04-20 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_auto_20200317_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='abacaction',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
        migrations.AddField(
            model_name='abacattribute',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
        migrations.AddField(
            model_name='abacdomain',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
        migrations.AddField(
            model_name='abacpolicy',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
        migrations.AddField(
            model_name='abacresource',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
        migrations.AddField(
            model_name='abacrule',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
        migrations.AddField(
            model_name='account',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
        migrations.AddField(
            model_name='accountrole',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Account'),
        ),
    ]