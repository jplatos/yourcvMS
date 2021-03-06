# Generated by Django 3.0.1 on 2020-06-22 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImportedRecordType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ImportedSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('issn', models.CharField(blank=True, max_length=20, null=True)),
                ('eissn', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(blank=True, max_length=40, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=40, null=True)),
                ('last_name', models.CharField(blank=True, max_length=40, null=True)),
                ('suffix', models.CharField(blank=True, max_length=40, null=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name', 'middle_name'],
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(blank=True, max_length=50, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('pages', models.CharField(blank=True, max_length=20, null=True)),
                ('doi', models.CharField(blank=True, max_length=100, null=True)),
                ('abstract', models.TextField(blank=True, null=True)),
                ('keywords', models.CharField(blank=True, max_length=100, null=True)),
                ('wos_id', models.CharField(blank=True, max_length=100, null=True)),
                ('scopus_id', models.CharField(blank=True, max_length=100, null=True)),
                ('wos_citation_count', models.IntegerField(blank=True, null=True)),
                ('scopus_citation_count', models.IntegerField(blank=True, null=True)),
                ('imported', models.BooleanField(default=False)),
                ('month', models.CharField(blank=True, max_length=20, null=True)),
                ('number', models.CharField(blank=True, max_length=20, null=True)),
                ('volume', models.CharField(blank=True, max_length=20, null=True)),
                ('conference', models.TextField(blank=True, null=True)),
                ('organized_from', models.DateField(blank=True, null=True)),
                ('organized_to', models.DateField(blank=True, null=True)),
                ('venue', models.CharField(blank=True, max_length=200, null=True)),
                ('series', models.CharField(blank=True, max_length=1000, null=True)),
                ('book_title', models.CharField(blank=True, max_length=200, null=True)),
                ('publisher', models.CharField(blank=True, max_length=100, null=True)),
                ('isbn', models.CharField(blank=True, max_length=50, null=True)),
                ('issn', models.CharField(blank=True, max_length=20, null=True)),
                ('journal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Journal')),
            ],
            options={
                'ordering': ['-year', 'title'],
            },
        ),
        migrations.CreateModel(
            name='PublicationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PublicationField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=40)),
                ('value', models.CharField(max_length=500)),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Publication')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='publication',
            name='publication_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.PublicationType'),
        ),
        migrations.AddField(
            model_name='journal',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Publisher'),
        ),
        migrations.CreateModel(
            name='ImportedRecordField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('value', models.TextField()),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.ImportedRecord')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='importedrecord',
            name='record_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.ImportedRecordType'),
        ),
        migrations.AddField(
            model_name='importedrecord',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.ImportedSource'),
        ),
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('index', models.IntegerField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Person')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Publication')),
            ],
            options={
                'ordering': ['index'],
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('index', models.IntegerField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Person')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Publication')),
            ],
            options={
                'ordering': ['index'],
            },
        ),
        migrations.CreateModel(
            name='AltName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yourcvMS.Person')),
            ],
        ),
    ]
