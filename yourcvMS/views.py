from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import View,TemplateView, CreateView, UpdateView, ListView, DetailView, DeleteView, FormView, RedirectView
from django.views.generic.detail import SingleObjectMixin
import django.db.transaction as transaction
from yourcvMS.models import *
from yourcvMS.forms import *
from yourcvMS.functions import *
import sys
import traceback
# Create your views here.


# Create your views here.
class IndexView(TemplateView):
    template_name = "yourcvMS/index.html"

    def get_context_data(self, **kwargs):
        context = {}
        context['person_count'] = Person.objects.all().count()
        context['publication_count'] = Publication.objects.all().count()
        context['journal_count'] = Journal.objects.all().count()
        context['publisher_count'] = Publisher.objects.all().count()
        return context

#######################################
#  Person
class PersonListView(ListView):
    model = Person
    
class PersonCreateView(CreateView):
    model = Person
    fields = ['first_name', 'middle_name', 'last_name', 'suffix']
    success_url = reverse_lazy('yourcvMS:person-list')


class PersonUpdateView(UpdateView):
    model = Person
    fields = ['first_name', 'middle_name', 'last_name', 'suffix']
    success_url = reverse_lazy('yourcvMS:person-list')

class PersonDetailView(DetailView):
    model = Person

class PersonDeleteView(DeleteView):
    model = Person
    success_url = reverse_lazy('yourcvMS:person-list')

class PersonMergeView(FormView):
    form_class = PersonMergeForm
    template_name = 'yourcvMS/person_merge_form.html'
    success_url = reverse_lazy('yourcvMS:person-list')

    def form_valid(self, form):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                # print(form.cleaned_data)
                primary = form.cleaned_data['primary_field']
                other = form.cleaned_data['other_field']

                merge_persons(primary, other)
            except :
                print('Error when handling file import for projects', sys.exc_info())
                pass
        return super().form_valid(form)


#######################################
#  PublicationType
#######################################

class PublicationTypeListView(ListView):
    model = PublicationType
   
class PublicationTypeCreateView(CreateView):
    model = PublicationType
    fields = ['key', 'name', 'czech_name']
    success_url = reverse_lazy('yourcvMS:publicationtype-list')

class PublicationTypeUpdateView(UpdateView):
    model = PublicationType
    fields = ['key', 'name', 'czech_name']
    success_url = reverse_lazy('yourcvMS:publicationtype-list')

class PublicationTypeDeleteView(DeleteView):
    model = PublicationType
    success_url = reverse_lazy('yourcvMS:publicationtype-list')


#######################################
#  Publication
#######################################

class PublicationListView(ListView):
    model = Publication
    queryset = Publication.objects.filter(imported=False)
    
class PublicationImportedListView(ListView):
    model = Publication
    queryset = Publication.objects.filter(imported=True)
    template_name = 'yourcvMS/publication_imported_list.html'


class PublicationUpdateView(UpdateView):
    model = Publication
    fields = [
        'publication_type', 'key', 'title', 'year', 'pages', 'doi', 'abstract', 'keywords', 'wos_id', 'scopus_id', 'wos_citation_count', 'scopus_citation_count', 'imported', 'journal', 'month', 'number', 'volume', 'conference', 'organized_from', 'organized_to', 'venue', 'series', 'booktitle', 'publisher', 'isbn', 'issn']
    success_url = reverse_lazy('yourcvMS:publication-list')

class PublicationSummaryView(TemplateView):
    
    template_name = 'yourcvMS/publication_summary.html'
    success_url = reverse_lazy('yourcvMS:publication-summary')
    content_type = 'text/html'

    type_template_content = {'latex':('yourcvMS/publication_summary.tex', 'text/html')}#'application/x-latex'

    def template_from_query(self):
        if 'type' in self.request.GET:
            typ = self.request.GET.get('type')
            if typ in self.type_template_content:
                return self.type_template_content[typ][0]
        return self.template_name

    def content_type_from_query(self):
        if 'type' in self.request.GET:
            typ = self.request.GET.get('type')
            if typ in self.type_template_content:
                return self.type_template_content[typ][1]
        return 'text/html'

    def get_template_names(self):
        return self.template_from_query()

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = self.content_type_from_query()    
        return super(TemplateView, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['publications'] = get_publication_counts()
        context['article_counts'], context['article_counts_map'] = get_publication_article_counts()
        context['article_list'] = get_publication_article_list()
        context['quartiles'], context['deciles'] = get_publication_quartiles_deciles()
        context['webofscience'] = get_publication_impact_factors()
        context['scimago'] = get_publication_scimago_factors()
        context['conference_counts'], context['conference_counts_map'] = get_publication_conference_counts()
        context['conference_list'] = get_publication_conference_list()
        # print(context)
        return context


class PublicationDetailView(DetailView):
    model = Publication    

class PublicationDeleteView(DeleteView):
    model = Publication
    success_url = reverse_lazy('yourcvMS:publication-list')

class PublicationApproveView(SingleObjectMixin, FormView):
    template_name = 'yourcvMS/publication_approve_form.html'
    form_class = PublicationApproveForm
    model = Publication
    success_url = reverse_lazy('yourcvMS:publication-imported-list')

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        # context[""] = 
        return context

    
    def form_valid(self, form):
        try:
            publication = self.get_object()
            publication.imported = False
            publication.save()
        except:
            print('Error when handling file approve publications', sys.exc_info())
        return super().form_valid(form)

class PublicationMergeView(FormView):
    form_class = PublicationMergeSingleSelectForm
    template_name = 'yourcvMS/publication_merge_select_form.html'
    success_url = reverse_lazy('yourcvMS:publication-imported-list')
    
    def get_initial(self):
        initial = super(FormView, self).get_initial()
        if 'pk' in self.kwargs:
            imported = get_object_or_404(Publication, pk=self.kwargs['pk'])
            initial['imported_field'] = imported
            most_similar = get_most_similar(imported)
            if most_similar:
                initial['original_field'] = most_similar
        return initial

    def form_valid(self, form):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                original = form.cleaned_data['original_field']
                imported = form.cleaned_data['imported_field']

                self.request.session['original'] = original.id
                self.request.session['imported'] = imported.id
                self.success_url = reverse_lazy('yourcvMS:publication-merge-final')
            except :
                print('Error when handling file import for projects', sys.exc_info())
                pass
        return super().form_valid(form)


class PublicationApproveAllView(FormView):
    template_name = 'yourcvMS/publication_approve_all_form.html'
    form_class = PublicationApproveForm
    success_url = reverse_lazy('yourcvMS:publication-list')
    
    @transaction.atomic
    def form_valid(self, form):
        try:
            publications = Publication.objects.filter(imported=True)
            for publication in publications:
                publication.imported = False
                publication.save()
        except:
            print('Error when handling file approve publications', sys.exc_info())
        return super().form_valid(form)


class PublicationMergeFinalView(FormView):
    form_class = PublicationMergeFinalForm
    template_name = 'yourcvMS/publication_merge_final_form.html'
    success_url = reverse_lazy('yourcvMS:publication-imported-list')

    def get_context_data(self, **kwargs):
        context = super(PublicationMergeFinalView, self).get_context_data(**kwargs)
        if 'original' in self.request.session:
            original_id = self.request.session['original']
            original = get_object_or_404(Publication, id=original_id)
        if 'imported' in self.request.session:
            imported_id = self.request.session['imported']
            imported = get_object_or_404(Publication, id=imported_id)

        o_dict, i_dict = original.__dict__, imported.__dict__
        fields = []
        for k, v in o_dict.items():
            if v is None and i_dict[k] is None:
                continue
            if v==i_dict[k]:
                continue
            if k.startswith('_') or k in ['id', 'imported', 'created', 'modified']:
                continue
            if i_dict[k] is None:
                continue
            fields.append((k.title(), k, v, i_dict[k]))
        context['fields'] = fields
        return context


    def form_valid(self, form):
        try:
            if 'original' in self.request.session:
                original_id = self.request.session['original']
                original = get_object_or_404(Publication, id=original_id)
            if 'imported' in self.request.session:
                imported_id = self.request.session['imported']
                imported = get_object_or_404(Publication, id=imported_id)
            
            o_dict, i_dict = original.__dict__, imported.__dict__
            fields = {}
            for k, v in o_dict.items():
                if v is None and i_dict[k] is None:
                    continue
                if v==i_dict[k]:
                    continue
                if k.startswith('_') or k in ['id', 'imported', 'created', 'modified']:
                    continue
                if i_dict[k] is None:
                    continue
                fields[k] = (v, i_dict[k])            
            
            for k, v in self.request.POST.items():
                if k.startswith('csrf'):
                    continue
                original.__dict__[k] = fields[k][int(v)]
                original.save()
            Publication.delete(imported)
        except :
            print('Error when handling file import for projects', sys.exc_info())
            pass
        return super().form_valid(form)


#######################################
#  Journal
#######################################
class JournalListView(ListView):
    model = Journal

    
class JournalUpdateView(UpdateView):
    model = Journal
    fields = ['title', 'publisher', 'issn', 'eissn']
    success_url = reverse_lazy('yourcvMS:journal-list')

class JournalDetailView(DetailView):
    model = Journal

class JournalDeleteView(DeleteView):
    model = Journal
    success_url = reverse_lazy('yourcvMS:journal-list')

class JournalGetRanking(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'yourcvMS:journal-detail'

    def get_redirect_url(self, *args, **kwargs):
        journal = get_object_or_404(Journal, pk=kwargs['pk'])
        rankings_get(journal)
        return super().get_redirect_url(*args, **kwargs)

class JournalYearRankDeleteView(DeleteView):
    model = JournalYearRank
    
    def get_success_url(self):
        return reverse_lazy('yourcvMS:journal-detail', kwargs = {'pk': self.object.journal.id })

class JournalClearRanking(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'yourcvMS:journal-detail'

    def get_redirect_url(self, *args, **kwargs):
        journal = get_object_or_404(Journal, pk=kwargs['pk'])
        rankings_clear(journal)
        return super().get_redirect_url(*args, **kwargs)

class JournalRefreshRanking(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'yourcvMS:journal-detail'

    def get_redirect_url(self, *args, **kwargs):
        journal = get_object_or_404(Journal, pk=kwargs['pk'])
        rankings_refresh(journal)
        return super().get_redirect_url(*args, **kwargs)


#######################################
#  Publisher
#######################################
class PublisherListView(ListView):
    model = Publisher

class PublisherNormalizeView(View):

    def get(self, request, *args, **kwargs):
        normalize_publisher_texts()
        return redirect(reverse('yourcvMS:publisher-list'))
    
class PublisherUpdateView(UpdateView):
    model = Publisher
    fields = ['name', 'address']
    success_url = reverse_lazy('yourcvMS:publisher-list')

class PublisherDetailView(DetailView):
    model = Publisher

class PublisherDeleteView(DeleteView):
    model = Publisher
    success_url = reverse_lazy('yourcvMS:publisher-list')


#######################################
#  ImportedRecord
#######################################
class ImportedRecordListView(ListView):
    model = ImportedRecord

    def get_context_data(self, **kwargs):
        context = {}
        context['source_list'] = ImportedSource.objects.all()
        context['type_list'] = ImportedRecordType.objects.all()
        context['importedrecord_list'] = ImportedRecord.objects.all()
        return context


class ImportedRecordImportBibView(FormView):
    form_class = ImportedRecordImportBibForm
    template_name = 'yourcvMS/importedrecord_importbib_form.html'
    success_url = reverse_lazy('yourcvMS:importedrecord-list')

    def form_valid(self, form):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                uploaded_field = form.cleaned_data['file_field']
                importedsource = form.cleaned_data['source_field']

                import_records_form_bib(uploaded_field, importedsource)
            except :
                print('Error when handling file import for projects', sys.exc_info())
                pass
        return super().form_valid(form)


class ImportedRecordDetailView(DetailView):
    model = ImportedRecord
    

class ImportedRecordDeleteView(DeleteView):
    model = ImportedRecord
    success_url = reverse_lazy('yourcvMS:importedrecord-list')

class ImportedSourceCreateView(CreateView):
    model = ImportedSource
    fields = ['name']
    success_url = reverse_lazy('yourcvMS:importedrecord-list')

class ImportedSourceDeleteView(DeleteView):
    model = ImportedSource


class ImportedRecordImportView(SingleObjectMixin, FormView):
    form_class = ImportedRecordImportForm
    template_name = 'yourcvMS/importedrecord_import_form.html'
    success_url = reverse_lazy('yourcvMS:importedrecord-list')
    model = ImportedRecord

    def get_initial(self):
        self.object = self.get_object()
        initial = super(FormView, self).get_initial()
        initial["template_field"] = get_template_by_record(self.object)
        
        return initial

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        
        authors_field = self.object.importedrecordfield_set.get(name='author')
        if authors_field:
            authors_str = authors_field.value
        if authors_str:
            authors = extract_unique_authors([authors_str])
            
            altname_map = {x.name:x.person.id for x in AltName.objects.all()}
            
            author_person = []
            for author in authors:
                if author in altname_map:
                    author_person.append((author, altname_map[author]))
                else:
                    author_person.append((author, 0))
            context['authors'] = author_person
        context['persons'] = Person.objects.all()
        
        return context

    def form_valid(self, form):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                record = self.get_object()
                template = form.cleaned_data["template_field"]
                # print(template)
                author_map = {x[3:]:self.request.POST[x] for x in self.request.POST.keys() if x.startswith("an_")}
                # print(author_map)
                import_record_by_template(record, template, author_map)
            except :
                print('Error when handling file import for projects', sys.exc_info())
                traceback.print_exc()
                pass
        return super().form_valid(form)


class ImportedRecordImportAllView(FormView):
    form_class = ImportedRecordImportAllForm
    template_name = 'yourcvMS/importedrecord_import_all_form.html'
    success_url = reverse_lazy('yourcvMS:importedrecord-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        records = ImportedRecord.objects.all()
        authors = []
        for record in records:
            authors_field = record.importedrecordfield_set.get(name='author')
            if authors_field:
                authors.append(authors_field.value)

        if authors:
            authors = extract_unique_authors(authors)
            
            altname_map = {x.name:x.person.id for x in AltName.objects.all()}
            
            author_person = []
            for author in authors:
                if author in altname_map:
                    author_person.append((author, altname_map[author]))
                else:
                    author_person.append((author, 0))
            context['authors'] = author_person
        context['persons'] = Person.objects.all()
        # print(context)
        return context

    def form_valid(self, form):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                records = ImportedRecord.objects.all()
        
                author_map = {x[3:]:self.request.POST[x] for x in self.request.POST.keys() if x.startswith("an_")}
                # print(author_map)
                import_record_all_by_template(records, author_map)
            except :
                print('Error when handling file import for projects', sys.exc_info())
                traceback.print_exc()
                pass
        return super().form_valid(form)

class ImportedRecordDeleteAllView(FormView):
    form_class = ImportedRecordDeleteAllForm
    template_name = 'yourcvMS/importedrecord_delete_all_form.html'
    success_url = reverse_lazy('yourcvMS:importedrecord-list')
    
    @transaction.atomic
    def form_valid(self, form):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                records = ImportedRecord.objects.all()

                for record in records:
                    ImportedRecord.delete(record)       
                
            except :
                print('Error when handling file import for projects', sys.exc_info())
                traceback.print_exc()
                pass
        return super().form_valid(form)


#######################################
#  ImportedRecordTemplate
#######################################
class ImportedRecordTemplateListView(ListView):
    model = ImportedRecordTemplate

class ImportedRecordTemplateDetailView(DetailView):
    model = ImportedRecordTemplate

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        publication_fields = ['key', 'title', 'year', 'pages', 'doi', 'abstract', 'keywords', 'wos_id', 'scopus_id', 'wos_citation_count', 'scopus_citation_count',
         'month', 'number', 'volume', 'conference', 'organized_from', 'organized_to', 'venue', 'series', 'booktitle', 'publisher', 'isbn', 'issn']

        record_fields = [x[0] for x in ImportedRecordField.objects.filter(record__source=self.object.source, record__record_type=self.object.record_type).values_list('name').distinct()]
                
        used_fields = {x.publication_field:(x.record_field,x.transform) for x in self.object.importedrecordtemplatefield_set.all()}
        
        fields = []
        for name in publication_fields:
            if not used_fields:
                fields.append((name, name, ''))
            elif name in used_fields:
                fields.append((name, used_fields[name][0], used_fields[name][1]))
            else:
                fields.append((name, '', ''))
        
        context["fields"] = fields
        context["record_fields"] = record_fields
    
        return context


class ImportedRecordTemplateFieldFormView(SingleObjectMixin, FormView):
    form_class = ImportedRecordTemplateFieldForm
    template_name = 'yourcvMS/importedrecordtemplate_detail.html'
    success_url = reverse_lazy('yourcvMS:importedrecordtemplate-list')
    model = ImportedRecordTemplate

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            template = self.get_object()
            used_fields = {x.publication_field:x for x in template.importedrecordtemplatefield_set.all()}
            for name, value in request.POST.items():
                if name.startswith('csrf') or name.endswith('_transform'):
                    continue
                if name in used_fields:
                    field = used_fields[name]
                    field.record_field = value
                    field.transform = request.POST[name+'_transform']
                    field.save()
                elif value:
                    field = template.importedrecordtemplatefield_set.create(publication_field=name, record_field=value, transform=request.POST[name+'_transform'])
        except:
            print('Error when handling file import for projects', sys.exc_info())
        finally:
            return super().post(request, *args, **kwargs)

class ImportedRecordTemplateCreateView(CreateView):
    model = ImportedRecordTemplate
    fields = ['name', 'source', 'record_type', 'publication_type', 'process_journal', 'filter_field', 'filter_value']
    success_url = reverse_lazy('yourcvMS:importedrecordtemplate-list')

class ImportedRecordTemplateUpdateView(UpdateView):
    model = ImportedRecordTemplate
    fields = ['name', 'source', 'record_type', 'publication_type', 'process_journal', 'filter_field', 'filter_value']
    success_url = reverse_lazy('yourcvMS:importedrecordtemplate-list')

class ImportedRecordTemplateDeleteView(DeleteView):
    model = ImportedRecordTemplate
    success_url = reverse_lazy('yourcvMS:importedrecordtemplate-list')

