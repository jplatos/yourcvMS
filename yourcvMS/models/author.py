from django.db import models

from . import TimeTracked, Person, Publication

class Author(TimeTracked):
    class Meta:
        ordering = ['index']

    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)    
    index = models.IntegerField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
