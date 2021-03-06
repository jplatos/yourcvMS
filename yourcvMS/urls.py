from django.urls import path

from . import views

app_name = 'yourcvMS'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('person/list', views.PersonListView.as_view(), name='person-list'),
    path('person/create', views.PersonCreateView.as_view(), name='person-create'),
    path('person/merge', views.PersonMergeView.as_view(), name='person-merge'),
    path('person/<int:pk>', views.PersonDetailView.as_view(), name='person-detail'),
    path('person/<int:pk>/update', views.PersonUpdateView.as_view(), name='person-update'),
    path('person/<int:pk>/delete', views.PersonDeleteView.as_view(), name='person-delete'),

    path('publication/list', views.PublicationListView.as_view(), name='publication-list'),
    path('publication/summary', views.PublicationSummaryView.as_view(), name='publication-summary'),
    path('publication/<int:pk>', views.PublicationDetailView.as_view(), name='publication-detail'),
    path('publication/<int:pk>/update', views.PublicationUpdateView.as_view(), name='publication-update'),
    path('publication/<int:pk>/delete', views.PublicationDeleteView.as_view(), name='publication-delete'),
    path('publication/<int:pk>/approve', views.PublicationApproveView.as_view(), name='publication-aprove'),
    path('publication/<int:pk>/merge', views.PublicationMergeView.as_view(), name='publication-merge'),
    
    path('publication/imported-list', views.PublicationImportedListView.as_view(), name='publication-imported-list'),
    path('publication/merge-final', views.PublicationMergeFinalView.as_view(), name='publication-merge-final'),
    path('publication/approve-all', views.PublicationApproveAllView.as_view(), name='publication-approve-all'),
    
    path('publication-type/list', views.PublicationTypeListView.as_view(), name='publicationtype-list'),
    path('publication-type/create', views.PublicationTypeCreateView.as_view(), name='publicationtype-create'),
    path('publication-type/<int:pk>/update', views.PublicationTypeUpdateView.as_view(), name='publicationtype-update'),
    path('publication-type/<int:pk>/delete', views.PublicationTypeDeleteView.as_view(), name='publicationtype-delete'),
    

    path('journal/list', views.JournalListView.as_view(), name='journal-list'),
    path('journal/<int:pk>', views.JournalDetailView.as_view(), name='journal-detail'),
    path('journal/<int:pk>/update', views.JournalUpdateView.as_view(), name='journal-update'),
    path('journal/<int:pk>/delete', views.JournalDeleteView.as_view(), name='journal-delete'),
    path('journal/<int:pk>/get-ranking', views.JournalGetRanking.as_view(), name='journal-get-ranking'),
    path('journal/<int:pk>/clear-ranking', views.JournalClearRanking.as_view(), name='journal-clear-ranking'),
    path('journal/<int:pk>/refresh-ranking', views.JournalRefreshRanking.as_view(), name='journal-refresh-ranking'),

    path('journal-year-rank/<int:pk>/delete', views.JournalYearRankDeleteView.as_view(), name='journal-year-rank-delete'),

    path('publisher/list', views.PublisherListView.as_view(), name='publisher-list'),
    path('publisher/normalize', views.PublisherNormalizeView.as_view(), name='publisher-normalize'),
    path('publisher/<int:pk>', views.PublisherDetailView.as_view(), name='publisher-detail'),
    path('publisher/<int:pk>/update', views.PublisherUpdateView.as_view(), name='publisher-update'),
    path('publisher/<int:pk>/delete', views.PublisherDeleteView.as_view(), name='publisher-delete'),

    path('imported-source/create', views.ImportedSourceCreateView.as_view(), name='importedsource-create'),
    path('imported-source/<int:pk>/delete', views.ImportedSourceDeleteView.as_view(), name='importedsource-delete'),
    path('imported-record/list', views.ImportedRecordListView.as_view(), name='importedrecord-list'),
    path('imported-record/<int:pk>', views.ImportedRecordDetailView.as_view(), name='importedrecord-detail'),
    path('imported-record/<int:pk>/import', views.ImportedRecordImportView.as_view(), name='importedrecord-import'),
    path('imported-record/<int:pk>/delete', views.ImportedRecordDeleteView.as_view(), name='importedrecord-delete'),
    path('imported-record/import-bib', views.ImportedRecordImportBibView.as_view(), name='importedrecord-import-bib'),
    path('imported-record/import-all', views.ImportedRecordImportAllView.as_view(), name='importedrecord-import-all'),
    path('imported-record/delete-all', views.ImportedRecordDeleteAllView.as_view(), name='importedrecord-delete-all'),

    path('imported-record-template/list', views.ImportedRecordTemplateListView.as_view(), name='importedrecordtemplate-list'),
    path('imported-record-template/create', views.ImportedRecordTemplateCreateView.as_view(), name='importedrecordtemplate-create'),
    path('imported-record-template/<int:pk>', views.ImportedRecordTemplateDetailView.as_view(), name='importedrecordtemplate-detail'),
    path('imported-record-template/<int:pk>/update-fields', views.ImportedRecordTemplateFieldFormView.as_view(), name='importedrecordtemplatefield-update'),
    path('imported-record-template/<int:pk>/update', views.ImportedRecordTemplateUpdateView.as_view(), name='importedrecordtemplate-update'),
    path('imported-record-template/<int:pk>/delete', views.ImportedRecordTemplateDeleteView.as_view(), name='importedrecordtemplate-delete'),
    
]