# Generated by Django 3.0.1 on 2020-08-26 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yourcvMS', '0010_auto_20200822_2240'),
    ]

    operations = [
        migrations.AddField(
            model_name='rankingsource',
            name='factor_shortcut',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='rankingsource',
            name='shortcut',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]