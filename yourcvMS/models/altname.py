
from django.db import models
from . import Person

class AltName(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)