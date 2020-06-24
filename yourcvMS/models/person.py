from django.db import models
from . import TimeTracked, TimeTracked

class Person(TimeTracked):
    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name']
        
    first_name = models.CharField(max_length=40, blank=True, null= True)
    middle_name = models.CharField(max_length=40, blank=True, null= True)
    last_name = models.CharField(max_length=40, blank=True, null= True)
    suffix = models.CharField(max_length=40, blank=True, null= True)
    
    @property
    def full_name(self):
        names = []
        if self.last_name:
            names.append(self.last_name)
        if self.first_name:
            names.append(self.first_name)
        if self.middle_name:
            names.append(self.middle_name)        
        return ' '.join(names)
    
    @property
    def short_name(self):
        names = []
        if self.last_name:
            names.append(self.last_name)
        if self.first_name:
            names.append(self.first_name[0]+'.')
        if self.middle_name:
            names.append(self.middle_name[0]+'.')
        return ' '.join(names)

    def __repr__(self):
        return self.full_name
    
    def __str__(self):
        return self.full_name