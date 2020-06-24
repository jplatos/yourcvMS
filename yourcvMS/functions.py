import bibtexparser
import django.db.transaction as transaction
from yourcvMS.models import Publication, Journal, Publisher, PublicationField, ImportedRecord, ImportedRecordField, ImportedRecordType

def extract_unique_authors(entries):
    result = set()
    for entry in entries:
        if 'author' in entry:
            names = entry['author'].replace('\n', ' ').replace('\r', ' ').split(' and ')
            for name in names:
                result.add(name.strip())
    return sorted(result)


@transaction.atomic
def import_publications(entries, author_map):

    def process_fields(entry):
        pub = Publication()
        fields = []
        for name, value in entry.items():
            value = value.lstrip('{').rstrip('}')
            if name=='ENTRYTYPE':
                if value in pubtypes_dict:
                    pub.publication_type = pubtypes_dict[value]
                else:                    
                    pt = PublicationType()
                    pt.name = value
                    pt.save()
                    pubtypes_dict[value] = pt
                    pub.publication_type = pt
            
            elif name=='unique-id':
                pub.key = value
                pub.wos_id = value
            elif name=='title':
                pub.title = value
            elif name=='book-title':
                pub.book_title = value
            elif name=='year':
                pub.year = value
            elif name=='pages':
                pub.pages = value
            elif name=='journal':
                jname = value
                address = entry['address'].lstrip('{').rstrip('}') if 'address' in entry else None
                
                publisher_name = entry['publisher'].lstrip('{').rstrip('}') if 'publisher' in entry else None
                if publisher_name:
                    try:
                        publisher = Publisher.objects.get(name=publisher_name)
                    except Publisher.DoesNotExist:
                        publisher = Publisher.objects.create(name=publisher_name, address=address)
                else:
                    publisher = None
                issn = entry['issn'].lstrip('{').rstrip('}') if 'issn' in entry else None
                eissn = entry['eissn'].lstrip('{').rstrip('}') if 'eissn' in entry else None
                try:
                    journal = Journal.objects.get(issn=issn)
                except Journal.DoesNotExist:                    
                    journal = Journal.objects.create(title=jname, issn=issn, eissn=eissn, publisher = publisher)
                pub.journal = journal

            elif name=='month':
                pub.month = value
            elif name=='number':
                pub.number = value
            elif name=='volume':
                pub.volume = value
            elif name=='url':
                pub.url = value
            elif name=='doi':
                pub.doi = value
            elif name=='abstract':
                pub.abstract = value
            elif name=='keywords':
                pub.keywords = value
            elif name=='isbn':
                pub.isbn = value
            elif name=='issn':
                pub.issn = value
            elif name=='address':
                pub.address = value
            elif name=='annotation':
                pub.annotation = value
            elif name=='chapter':
                pub.chapter = value
            elif name=='cross-ref':
                pub.cross_ref = value
            elif name=='edition':
                pub.edition = value
            elif name=='institution':
                pub.institution = value
            elif name=='note':
                pub.note = value
            elif name=='organization':
                pub.organization = value
            elif name=='publisher':
                pub.publisher = value
            elif name=='school':
                pub.school = value
            elif name=='series':
                pub.series = value
            elif name=='specific_type':
                pub.specific_type = value
            elif name=='times_cited':
                pub.wos_citation_count = int(value)
            else:
                fields.append((name,value))

        return pub, fields
    
    pubtypes = PublicationType.objects.all()
    pubtypes_dict = {x.name:x for x in pubtypes}
    altnames = AltName.objects.all()
    altnames_dict = {x.name:x for x in altnames}

    person_map = {x.id:x for x in Person.objects.all()}
    for entry in entries:
        pub, fields = process_fields(entry)
        pub.imported = True
        authors = extract_unique_authors([entry])
        pub.save()
        for name, value in fields:
            PublicationField.objects.create(publication=pub, name=name, value=value)
        for idx, author in enumerate(authors):
            person_id = int(author_map[author])
            if person_id==0:
                if author in altnames_dict:
                    person = altnames_dict[author]
                    person_id = person.id
                else:
                    first = ''
                    last = author
                    if ',' in author:
                        last, first = author.split(',')
                    person = Person.objects.create(last_name=last.strip(), first_name = first.strip())
                    person_map[person.id] = person
                    person_id = person.id
            if author not in altnames_dict:
                altname = AltName.objects.create(name=author, person=person_map[person_id])
                altnames_dict[author] = person_map[person_id]
                
            Author.objects.create(index=idx, person=person_map[person_id], publication=pub)
    


def parse_bib_file(uploaded_file):
    if uploaded_file.content_type =='application/octet-stream' and uploaded_file.name.endswith('.bib'):
        content = uploaded_file.read()  
        bib_database = bibtexparser.loads(content) 
        return bib_database.entries
    else:
        return None

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

def publication_remove_eol():
    print('Remove EoL from publication titles')
    for pub in Publication.objects.filter(imported=False):
        if '\r' in pub.title or '\n' in pub.title:
            pub.title = pub.title.replace('\r',' ').replace('\n', ' ')
            pub.save()


@transaction.atomic
def import_records(uploaded_file, importedsource):
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
    