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

class RankingSource(TimeTracked):
    name = models.CharField(max_length=100, blank=True, null=True)
    shortcut = models.CharField(max_length=20, blank=True, null=True)
    factor_name = models.CharField(max_length=100, blank=True, null=True)
    factor_shortcut = models.CharField(max_length=100, blank=True, null=True)
   

class JournalYearRank(TimeTracked):
    class Meta:
        ordering = ['-year']
        
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)
    year = models.IntegerField()
    centil_average = models.IntegerField()
    rank_average = models.IntegerField()
    number_of_journals = models.IntegerField()

    def __str__(self):
        return f'{self.journal} - {self.year} - {self.centil_average} - {self.rank_average} - {self.number_of_journals}'

    @property
    def decil_average(self):
        return 1+(self.centil_average // 10)

    @property
    def quartil_average(self):
        return 1+(self.centil_average // 25)

class JournalSourceYearRank(TimeTracked):
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)
    source = models.ForeignKey(RankingSource, on_delete=models.PROTECT)
    year = models.IntegerField()
    centil_average = models.IntegerField()
    rank_average = models.IntegerField()
    number_of_journals = models.IntegerField()
    factor = models.FloatField()

class JournalSourceYearCategory(TimeTracked):
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)
    source = models.ForeignKey(RankingSource, on_delete=models.PROTECT)
    category = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField()
    centil = models.IntegerField()
    rank = models.IntegerField()
    number_of_journals = models.IntegerField()


