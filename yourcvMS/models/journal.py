from django.db import models

from . import TimeTracked, Publisher

class Journal(TimeTracked):

    class Meta:
        ordering = ['title']

    title = models.CharField(max_length=200)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, blank=True, null=True)
    issn = models.CharField(max_length=20, blank=True, null=True)
    eissn = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.title