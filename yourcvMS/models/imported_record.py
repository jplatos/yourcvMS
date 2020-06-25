from django.db import models
from . import TimeTracked, PublicationType

class ImportedSource(TimeTracked):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name



class ImportedRecordType(TimeTracked):
    class Meta:
        ordering = ['name']
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ImportedRecord(TimeTracked):
    source = models.ForeignKey(ImportedSource, on_delete=models.CASCADE)
    record_type = models.ForeignKey(ImportedRecordType, on_delete=models.CASCADE)

    def __str__(self):
        if self.importedrecordfield_set:
            for field in self.importedrecordfield_set.all():
                if field.name=='title':
                    return field.value
        return '-----'


class ImportedRecordField(TimeTracked):
    record = models.ForeignKey(ImportedRecord, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    value = models.TextField()

    def __str__(self):
        return f'{self.name} - {self.value}'


class ImportedRecordTemplate(TimeTracked):
    class Meta:
        ordering = ['source', 'record_type']

    name = models.CharField(max_length=100)

    source = models.ForeignKey(ImportedSource, on_delete=models.CASCADE)
    record_type = models.ForeignKey(ImportedRecordType, on_delete=models.CASCADE)

    publication_type = models.ForeignKey(PublicationType, on_delete=models.CASCADE)
    process_journal = models.BooleanField(default=False)
    filter_field = models.CharField(max_length=50, blank=True, null=True)
    filter_value = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.source.name} - {self.record_type.name} => {self.publication_type.name}'


class ImportedRecordTemplateField(TimeTracked):
    template = models.ForeignKey(ImportedRecordTemplate, on_delete=models.CASCADE)

    publication_field = models.CharField(max_length=100, blank=True, null=True)
    record_field = models.CharField(max_length=100, blank=True, null=True)
    transform = models.CharField(max_length=200, blank=True, null=True)

