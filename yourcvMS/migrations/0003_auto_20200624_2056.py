# Generated by Django 3.0.1 on 2020-06-24 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yourcvMS', '0002_importedrecordtemplate_importedrecordtemplatefield'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='importedrecordtemplate',
            options={'ordering': ['source', 'record_type']},
        ),
        migrations.AddField(
            model_name='importedrecordtemplate',
            name='filter_field',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='importedrecordtemplate',
            name='filter_value',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='importedrecordtemplate',
            name='name',
            field=models.CharField(default='TEST', max_length=100),
            preserve_default=False,
        ),
    ]
