from django.db import models
from . import Publication, TimeTracked

class PublicationField(TimeTracked):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    value = models.CharField(max_length=500)