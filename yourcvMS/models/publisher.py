from django.db import models
from . import TimeTracked

class Publisher(TimeTracked):

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.name}, {self.address}'
