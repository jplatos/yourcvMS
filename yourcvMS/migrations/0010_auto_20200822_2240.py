# Generated by Django 3.0.1 on 2020-08-22 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yourcvMS', '0009_auto_20200809_2216'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='journalyearrank',
            options={'ordering': ['-year']},
        ),
        migrations.AddField(
            model_name='publicationtype',
            name='czech_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]