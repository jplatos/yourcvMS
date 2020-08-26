from django.db import models
from . import TimeTracked

class PublicationType(TimeTracked):
    class Meta:
        ordering = ['name']
        
    key = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=50)
    czech_name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    