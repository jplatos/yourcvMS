from django.db import models
from . import TimeTracked

class PublicationType(TimeTracked):
    class Meta:
        ordering = ['name']
        
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    