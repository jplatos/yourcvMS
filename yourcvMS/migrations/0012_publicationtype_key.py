# Generated by Django 3.0.1 on 2020-08-26 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yourcvMS', '0011_auto_20200826_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationtype',
            name='key',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
