from django import forms
from .models import Person, Publication, ImportedSource, ImportedRecordTemplate

class PublicationImportForm(forms.Form):
    file_field = forms.FileField()
    
class PersonMergeForm(forms.Form):
    primary_field = forms.ModelChoiceField(queryset=Person.objects.all())
    other_field = forms.ModelChoiceField(queryset=Person.objects.all())

class PublicationMergeSingleSelectForm(forms.Form):
    imported_field = forms.ModelChoiceField(queryset=Publication.objects.filter(imported=True), disabled=True)
    original_field = forms.ModelChoiceField(queryset=Publication.objects.filter(imported=False).order_by('title'))


class PublicationMergeFinalForm(forms.Form):    
    pass

class ImportedRecordImportBibForm(forms.Form):
    file_field = forms.FileField()
    source_field = forms.ModelChoiceField(queryset=ImportedSource.objects.all())

class ImportedRecordImportForm(forms.Form):    
    template_field = forms.ModelChoiceField(queryset=ImportedRecordTemplate.objects.all())
    pass

class ImportedRecordImportAllForm(forms.Form):   
    pass

class ImportedRecordDeleteAllForm(forms.Form):   
    pass

class ImportedRecordTemplateFieldForm(forms.Form):    
    pass

class PublicationApproveForm(forms.Form):
    pass
