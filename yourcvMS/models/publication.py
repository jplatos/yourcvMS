from django.db import models

from . import TimeTracked, PublicationType, Journal

class Publication(TimeTracked):

    class Meta:
        ordering = ['-year', 'title']

    # type of the publication
    publication_type = models.ForeignKey(PublicationType, on_delete=models.PROTECT)
    
    # A hidden field used for specifying or overriding the alphabetical order of entries (when the "author" and "editor" fields are missing). Note that this is very different from the key (mentioned just after this list) that is used to cite or cross-reference the entry.
    key = models.CharField(max_length=50, blank=True, null= True)

    # The title of the work.
    title = models.CharField(max_length=200, blank=True, null= True)

    # The year of publication (or, if unpublished, the year of creation).
    year = models.IntegerField(blank=True, null=True)

    # Page numbers, separated either by commas or double-hyphens.
    pages = models.CharField(max_length=20, blank=True, null= True)

    # Doi of the record
    doi = models.CharField(max_length=100, blank=True, null= True)

    # abstract of the paper
    abstract = models.TextField(blank=True, null=True)

    # keywords
    keywords = models.CharField(max_length=100, blank=True, null=True)

    # web of science and scopus unique id - WOS number or eID (Scopus)
    wos_id = models.CharField(max_length=100, blank=True, null=True)
    scopus_id = models.CharField(max_length=100, blank=True, null=True)

    # numbe rof citation on WoS and/or Scopus
    wos_citation_count = models.IntegerField(blank=True, null=True)
    scopus_citation_count = models.IntegerField(blank=True, null=True)
    
    # is the publication still in imported state
    imported = models.BooleanField(default=False)

    ########################################################
    # Journals
    ########################################################

    # The journal or magazine the work was published in
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT, blank=True, null=True)
    
    # The month of publication (or, if unpublished, the month of creation)
    month = models.CharField(max_length=20, blank=True, null= True)

    # The "(issue) number" of a journal, magazine, or tech-report, if applicable. (Most publications have a "volume", but no "number" field.)
    number = models.CharField(max_length=20, blank=True, null= True)

    # The volume of a journal or multi-volume book.
    volume = models.CharField(max_length=20, blank=True, null= True)

    
    ########################################################
    # Inproceedings, book
    ########################################################

    conference = models.TextField(blank=True, null= True)

    organized_from = models.DateField(blank=True, null= True)

    organized_to = models.DateField(blank=True, null= True)

    venue = models.CharField(max_length=200, blank=True, null= True)

    # The series of books the book was published in (e.g. "The Hardy Boys" or "Lecture Notes in Computer Science").
    series = models.CharField(max_length=1000, blank=True, null= True)    
    
    # The title of the book, if only part of it is being cited
    booktitle = models.CharField(max_length=200, blank=True, null= True)

    # The publisher's name
    publisher = models.CharField(max_length=100, blank=True, null= True)
        
    isbn = models.CharField(max_length=50, blank=True, null=True)
    
    issn = models.CharField(max_length=20, blank=True, null=True)

    
    @property
    def authors_str(self):
        persons =[]
        for author in self.author_set.all():
            persons.append(author.person)
        return ', '.join([x.short_name for x in persons])

    @property
    def source_str(self):
        parts = []
        if self.journal:
            parts.append(self.journal.title)
        elif self.series:
            parts.append(self.series)
        if self.booktitle:
            parts.append(self.booktitle)
        if self.volume:
            if self.number:
                parts.append('{}({})'.format(self.volume, self.number))
            else:
                parts.append('{}'.format(self.volume))
        if self.pages:
            parts.append('pages {}'.format(self.pages))
        if self.month:
            parts.append(self.month)
        if self.year:
            parts.append(str(self.year))
        return ', '.join(parts)+'.'
    
    def __str__(self):
        return f'{self.title}, {self.source_str}'