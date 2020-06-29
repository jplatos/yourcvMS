import bibtexparser
import django.db.transaction as transaction
from yourcvMS.models import Publication, Journal, Publisher, PublicationField, ImportedRecord, ImportedRecordField, ImportedRecordType, ImportedRecordTemplate, AltName, Person
from .helpers import *

def extract_unique_authors(authors_list):
    result = set()
    for authors in authors_list:
        names = authors.replace('\n', ' ').replace('\r', ' ').split(' and ')
        for name in names:
            result.add(name.strip())
    return sorted(result)


def merge_persons(primary, other):
    for author in other.author_set.all():
        author.person = primary
        author.save()
    Person.delete(other)

def normalize_journal_titles():
    print('Normalize titles journal')
    for journal in Journal.objects.all():
        print(journal.title+ ' - ', end='')
        journal.title = journal.title.title()
        print(journal.title)
        if '\&' in journal.title:
            journal.title = journal.title.replace('\&', '&')
        journal.save()

def normalize_publisher_texts():
    for publisher in Publisher.objects.all():
        publisher.name = publisher.name.title()
        publisher.address = publisher.address.title()
        publisher.save()

def remove_imported_by_name():
    name_pub = {}
    for pub in Publication.objects.filter(imported=False):
        name_pub[pub.title.lower()] = pub

    for pub in Publication.objects.filter(imported=True):
        key = pub.title.lower()
        if key in name_pub:
            Publication.delete(pub)


@transaction.atomic
def import_records_form_bib(uploaded_file, importedsource):
    if uploaded_file.content_type =='application/octet-stream' and uploaded_file.name.endswith('.bib'):
        content = uploaded_file.read()  
        bib_database = bibtexparser.loads(content) 
        
        rectypes = ImportedRecordType.objects.all()
        rectypes = {x.name:x for x in rectypes}
        for entry in bib_database.entries:
            record_type = None
            record = None
            fields = []
            for name, value in entry.items():
                value = value.lstrip('{').rstrip('}').replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
                if name=='ENTRYTYPE':
                    if value in rectypes:
                        record_type = rectypes[value]
                    else:                    
                        pt = ImportedRecordType(name=value)
                        pt.save()
                        rectypes[value] = pt
                        record_type = pt
                    record = ImportedRecord.objects.create(source = importedsource, record_type=record_type)
                else:
                    fields.append((name, value))
            if record:
                for name, value in fields:
                    ImportedRecordField.objects.create(record=record, name=name, value=value)

    return
    

def get_template_by_record(record):
    templates = ImportedRecordTemplate.objects.filter(source=record.source, record_type = record.record_type)
    
    if templates:
        for template in templates:
            if template.filter_field:
                try:
                    field = record.importedrecordfield_set.get(name=template.field_field)
                    if template.filter_value == field.value:
                        return template
                except:
                    pass
            else:
                return template
    return None


@transaction.atomic
def import_record_by_template(record, template, author_map):
    
    record_fields = {x.name:x.value for x in record.importedrecordfield_set.all()}

    pub = Publication()
    pub.publication_type = template.publication_type

    # process fields from the template and assign it to the publication
    for field in template.importedrecordtemplatefield_set.all():
        if field.record_field in record_fields:
            pub.__dict__[field.publication_field] = record_fields[field.record_field]
    
    # process journal is required.
    if template.process_journal and 'journal' in record_fields:
        jname = titlelize(record_fields['journal'])
        address = record_fields['address'].lstrip('{').rstrip('}') if 'address' in record_fields else None
        
        publisher_name = record_fields['publisher'].lstrip('{').rstrip('}') if 'publisher' in record_fields else None
        if publisher_name:
            publisher_name = titlelize(publisher_name)
            try:
                publisher = Publisher.objects.get(name=publisher_name)
            except Publisher.DoesNotExist:
                publisher = Publisher.objects.create(name=publisher_name, address=address)
        else:
            publisher = None
        issn = record_fields['issn'].lstrip('{').rstrip('}') if 'issn' in record_fields else None
        if issn:
            issn = normalize_issn(issn)
        eissn = record_fields['eissn'].lstrip('{').rstrip('}') if 'eissn' in record_fields else None
        if eissn:
            eissn = normalize_issn(eissn)
        try:
            journal = Journal.objects.get(issn=issn)
        except Journal.DoesNotExist:                    
            journal = Journal.objects.create(title=jname, issn=issn, eissn=eissn, publisher = publisher)
        pub.journal = journal
    
    if pub.title:
        pub.title = titlelize(pub.title)

    pub.imported = True
    pub.save()

    # process authors of the publication
    if 'author' in record_fields:
        names = extract_unique_authors([record_fields['author']])
        for idx, author in enumerate(names):
            person_id = int(author_map[author])
            if person_id==0:
                first = ''
                last = author
                if ',' in author:
                    last, first = author.split(',')
                person = Person.objects.create(last_name=last.strip(), first_name = first.strip())
                author_map[author] = person.id
            else:   
                person = Person.objects.get(pk=person_id)
                
            pub.author_set.create(index=idx, person=person)

            altname, _ = AltName.objects.get_or_create(name=author, defaults={'person':person})

    # copy all record fields to publication fields for later processing
    for name, value in record_fields.items():
        pub.publicationfield_set.create(name=name, value=value)

    ImportedRecord.delete(record)
    return



@transaction.atomic
def import_record_all_by_template(records, author_map):
    
    for record in records:
        template = get_template_by_record(record)
        
        if not template:
            continue

        import_record_by_template(record, template, author_map)

    return