from django import forms
from .models import Person, Publication, ImportedSource

class PublicationImportForm(forms.Form):
    file_field = forms.FileField()
    
class PersonMergeForm(forms.Form):
    primary_field = forms.ModelChoiceField(queryset=Person.objects.all())
    other_field = forms.ModelChoiceField(queryset=Person.objects.all())

class PublicationMergeSelectForm(forms.Form):
    imported_field = forms.ModelChoiceField(queryset=Publication.objects.filter(imported=True))
    original_field = forms.ModelChoiceField(queryset=Publication.objects.filter(imported=False))
    
class PublicationMergeFinalForm(forms.Form):    
    pass

class ImportedRecordImportForm(forms.Form):
    file_field = forms.FileField()
    source_field = forms.ModelChoiceField(queryset=ImportedSource.objects.all())

class ImportedRecordTemplateFieldForm(forms.Form):    
    pass
