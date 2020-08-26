import bibtexparser
import django.db.transaction as transaction
from django.db.models import Count
from yourcvMS.models import Publication, Journal, Publisher, PublicationField, ImportedRecord, ImportedRecordField, ImportedRecordType, ImportedRecordTemplate, AltName, Person, JournalYearRank, JournalSourceYearRank, JournalSourceYearCategory, RankingSource, PublicationType
from .helpers import *
import sys
import traceback
from urllib.parse import urlparse, parse_qs
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

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

def normalize_publisher_texts():
    for publisher in Publisher.objects.all():
        publisher.name = titlelize(publisher.name)
        if publisher.address:
            publisher.address = titlelize(publisher.address)
        publisher.save()


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
    # print(templates)
    if templates:
        for template in templates:
            # print(template)
            if template.filter_field:
                try:
                    field = record.importedrecordfield_set.get(name=template.filter_field)
                    # print(field)
                    if template.filter_value == field.value:
                        return template
                except:
                    print('Error when handling file import for projects', sys.exc_info())
                    traceback.print_exc()
                    pass
            else:
                return template
    return None

def process_transform(value, transform):
    steps = transform.split(' ')
    if steps[0] == 'skip':
        to_skip = int(steps[1])
        value = value[to_skip:]
        if len(steps)>2:
            if steps[2] == 'ends':
                end_symbol = steps[3]
                if end_symbol in value:
                    value = value[:value.index(end_symbol)]
        return value.strip()
    elif steps[0] == 'starts':
        end_symbol = steps[1]
        if end_symbol in value:
            value = value[value.index(end_symbol)+1:]
        return value.strip()
    elif steps[0] == 'url':
        result = urlparse(value)
        # print(result)
        if result.query:
            params = parse_qs(result.query)
            # print(params)
            if steps[1] in params:
                values = params[steps[1]]
                if isinstance(values, list):
                    return values[0]
                else:
                    return values


@transaction.atomic
def import_record_by_template(record, template, author_map):
    
    record_fields = {x.name:x.value for x in record.importedrecordfield_set.all()}

    pub = Publication()
    pub.publication_type = template.publication_type

    # process fields from the template and assign it to the publication
    for field in template.importedrecordtemplatefield_set.all():
        if field.record_field in record_fields:
            if field.transform:
                pub.__dict__[field.publication_field] = process_transform(record_fields[field.record_field], field.transform)
            else:
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

    if pub.isbn:
        pub.isbn = normalize_isbn(pub.isbn)
    if pub.issn:
        pub.issn = normalize_issn(pub.issn)

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
            
            # AltName.objects.create(name=author, person=person)
            altname, created = AltName.objects.get_or_create(name__exact=author, defaults={'name':author, 'person':person})
            if created:
                print(f'Created {author} - {person}')

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


def get_most_similar(original):
    publications = Publication.objects.filter(imported=False)

    for pub in publications:
        if pub.title == original.title:
            return pub
    return None



def get_journal_ranking_from_service_xml(issn, year):
    try:
        url = f'https://db.cs.vsb.cz/scis/journals/journalhandler.ashx?cmd=journalInfo&searchstring={issn}&year={year}'
        # url = f'https://db.cs.vsb.cz/scis/journals/journalhandler.ashx?cmd=journalInfo&searchstring={issn}&year=0&closestYear=yes'
        # url = f'http://dbsys.cs.vsb.cz/scis/journals/journalhandler.ashx?cmd=journalInfo&searchstring={issn}&year={year}'
        print(url)
        contents = urllib.request.urlopen(url).read()
        # print(contents)
        return contents
    except:
        return None

def process_journal_ranking_xml(data, journal, year):
    root = ET.fromstring(data)
    
    for element in root:
        if element.tag in ('ScimagoJR', 'WebOfScience'):
            ranking_name = element.tag
            factor_name = element[0].tag
            ranking, created = RankingSource.objects.get_or_create(name=ranking_name, factor_name=factor_name)
            # print(ranking)
            # print(element[0].text)
            factor = float(element[0].text)
            categories = element[1]
            # year = element[2]
            rank_avg = int(element[3].text)
            number_journals = int(element[4].text)
            centil_avg = int(element[5].text)
            jsyr, created = JournalSourceYearRank.objects.get_or_create(journal=journal, year=year, source=ranking, 
                defaults={'centil_average':centil_avg, 'rank_average':rank_avg, 'number_of_journals':number_journals, 'factor':factor})
            jsyr.centil_average = centil_avg
            jsyr.rank_average = rank_avg
            jsyr.number_of_journals = number_journals
            jsyr.factor = factor
            jsyr.save()

            for category in categories:
                name = category[0].text
                journal_rank = int(category[1].text)
                number_of_journals = int(category[2].text)
                centil = int(category[3].text)
                jsyc, created = JournalSourceYearCategory.objects.get_or_create(journal=journal, year=year, source=ranking, category=name, 
                    defaults = {'centil':centil, 'rank':journal_rank, 'number_of_journals':number_of_journals})
                jsyc.centil = centil
                jsyc.rank = journal_rank
                jsyc.number_of_journals = number_of_journals
                jsyc.save()
            
        if element.tag=='Summary':
            summary = element
            jyr = JournalYearRank(journal=journal, year=year)
            for child in summary:
                if child.tag=='NumberOfJournalsAvg':
                    jyr.number_of_journals = int(child.text)
                if child.tag=='RankAvg':
                    jyr.rank_average = int(child.text)
                if child.tag=='CentilAvg':
                    jyr.centil_average = int(child.text)
            jyr.save()




def rankings_get(journal):
    years = set()
    for publication in journal.publication_set.all():
        years.add(publication.year)
    yearranking = {x.year:x for x in journal.journalyearrank_set.all()}
    print(f'Year: {years}')
    print(f'Year ranking: {yearranking}')
    for year in sorted(years):
        if year in yearranking:
            continue
        data = get_journal_ranking_from_service_xml(journal.issn, year)
        if not data:
            year = year-1
            if year in yearranking: continue
            data = get_journal_ranking_from_service_xml(journal.issn, year)
        if data:
            process_journal_ranking_xml(data, journal, year)

def rankings_clear(journal):
    JournalSourceYearCategory.objects.filter(journal=journal).delete()
    JournalSourceYearRank.objects.filter(journal=journal).delete()
    JournalYearRank.objects.filter(journal=journal).delete()

def rankings_refresh(journal):
    rankings_clear(journal)
    rankings_get(journal)



def get_publication_counts():
    counts = Publication.objects.order_by('publication_type').values('publication_type__key', 'publication_type__name', 'publication_type__czech_name').annotate(total=Count('id'))
    
    result = [{
        'count':result['total'],
        'name':result['publication_type__name'],
        'czech_name':result['publication_type__czech_name']
        } 
        for result in counts]
    
    return result


def get_publication_quartiles_deciles():
    try:
        journal_type = PublicationType.objects.get(name__icontains='journal')
        # print(journal_type)
    except:
        print('Failed to get journal publication type')
        return [], []

    articles = Publication.objects.filter(publication_type=journal_type)
    
    quartiles = [0 for x in range(4)]
    deciles = [0 for x in range(10)]
    
    for article in articles:
        year = article.year
        journal = article.journal
        ranks = JournalYearRank.objects.filter(journal=journal, year__lte=year).order_by('-year')
        
        if ranks and ranks.count()>0:
            current = ranks[0]
            if current.year==year or current.year==year-1:
                quartiles[current.quartil_average-1] += 1
                deciles[current.decil_average-1] += 1
            else:
                print(journal, year)
        else:
            print(journal, year)

    return quartiles, deciles


def get_publication_article_counts():
    try:
        journal_type = PublicationType.objects.get(name__icontains='journal')
        # print(journal_type)
    except:
        print('Failed to get journal publication type')
        return [], []

    articles = Publication.objects.filter(publication_type=journal_type)
    
    counts = {}

    for article in articles:
        year = article.year
        journal = article.journal
        ranks = JournalSourceYearRank.objects.filter(journal=journal, year__lte=year).order_by('-year')
        used_ranks = set()
        for rank in ranks:
            if rank.year==year or rank.year==year-1:
                if rank.source.name not in used_ranks:
                    used_ranks.add(rank.source.name)
                    if rank.source not in counts:
                        counts[rank.source] = 0
                    counts[rank.source] += 1
    as_list = [(source.name, count) for source, count in counts.items()]
    print(as_list)
    as_dict= {source.shortcut.lower():{'name':source.name, 'shortcut':source.shortcut, 'count':count} for source, count in counts.items()}
    print(as_dict)
    return as_list, as_dict 


def get_publication_impact_factors():
    try:
        journal_type = PublicationType.objects.get(name__icontains='journal')
        # print(journal_type)
    except:
        print('Failed to get journal publication type')
        return [], []

    articles = Publication.objects.filter(publication_type=journal_type)
    
    ranking = RankingSource.objects.get(name='WebOfScience')

    thresholds = [5, 3, 1, 0]
    factors = [0, 0, 0, 0]
    
    for article in articles:
        year = article.year
        journal = article.journal
        ranks = JournalSourceYearRank.objects.filter(journal=journal, source=ranking, year__lte=year).order_by('-year')
        
        if ranks and ranks.count()>0:
            current = ranks[0]
            if current.year==year or current.year==year-1:
                factor = current.factor
                for idx, t in enumerate(thresholds):
                    if factor>=t:
                        factors[idx] += 1
                        break
                # factors.append(current.factor)
        #     else:
        #         print(journal, year)
        # else:
        #     print(journal, year)

    return [(t,f) for t, f in zip(thresholds,factors)]

def get_publication_scimago_factors():
    try:
        journal_type = PublicationType.objects.get(name__icontains='journal')
        # print(journal_type)
    except:
        print('Failed to get journal publication type')
        return [], []

    articles = Publication.objects.filter(publication_type=journal_type)
    
    ranking = RankingSource.objects.get(name='ScimagoJR')

    thresholds = [2, 1, 0.5, 0]
    factors = [0, 0, 0, 0]
    
    for article in articles:
        year = article.year
        journal = article.journal
        ranks = JournalSourceYearRank.objects.filter(journal=journal, source=ranking, year__lte=year).order_by('-year')
        
        if ranks and ranks.count()>0:
            current = ranks[0]
            if current.year==year or current.year==year-1:
                factor = current.factor
                for idx, t in enumerate(thresholds):
                    if factor>=t:
                        factors[idx] += 1
                        break
        #     else:
        #         print(journal, year)
        # else:
        #     print(journal, year)

    return [(t,f) for t, f in zip(thresholds,factors)]


def get_publication_article_list():
    try:
        journal_type = PublicationType.objects.get(name__icontains='journal')
        # print(journal_type)
    except:
        print('Failed to get journal publication type')
        return [], []

    articles = Publication.objects.filter(publication_type=journal_type)
    
    result = []
    
    for article in articles:   
        meta = {}

        # source factors  
        factors = []
        year = article.year
        journal = article.journal
        ranks = JournalSourceYearRank.objects.filter(journal=journal, year__lte=year).order_by('-year', '-source')
        used_ranks = set()
        used_source_years = []
        for rank in ranks:
            if rank.year==year or rank.year==year-1:
                if rank.source.name not in used_ranks:
                    used_ranks.add(rank.source.name)
                    used_source_years.append((rank.source, rank.year))
                    factors.append(f'{rank.source.factor_shortcut}: {rank.factor}/{rank.year}')
        meta['factors'] = ', '.join(factors)

        # percentils  
        factors = []
        year = article.year
        journal = article.journal
        ranks = JournalYearRank.objects.filter(journal=journal, year__lte=year).order_by('-year')
        for rank in ranks:
            if rank.year==year or rank.year==year-1:
                meta['centile'] = f'{rank.centil_average}'

        # categories
        all_categories = []
        for source, year in used_source_years:
            categories = JournalSourceYearCategory.objects.filter(journal=article.journal, year=year, source=source).order_by('-category')
            all_categories.extend([x.category for x in categories])
            if all_categories:
                all_categories[-1] = all_categories[-1]+f' ({source.shortcut})'
        meta['categories'] = ', '.join(all_categories)

        # citations
        cit = []
        if article.wos_citation_count and article.wos_citation_count>0:
            cit.append(f'{article.wos_citation_count} (WoS)')
        if article.scopus_citation_count and article.scopus_citation_count>0:
            cit.append(f'{article.scopus_citation_count} (Scopus)')
        meta['citations'] = ', '.join(cit)

        result.append((article, meta))

    return result


def get_publication_conference_counts():
    try:
        conference_type = PublicationType.objects.get(name__icontains='conference')
        # print(journal_type)
    except:
        print('Failed to get journal publication type')
        return [], []

    articles = Publication.objects.filter(publication_type=conference_type)
    
    counts = {'wos':0, 'scopus':0}
    names = {'wos':'Web of Sciene', 'scopus':'Scopus'}
    for article in articles:
        if article.wos_id:
            counts['wos'] += 1
        if article.scopus_id:
            counts['scopus'] += 1
    as_list = [(names[name], count) for name, count in counts.items()]
    # print(as_list)
    as_dict= {name:{'name':names[name], 'count':count} for name, count in counts.items()}
    # print(as_dict)
    return as_list, as_dict 


def get_publication_conference_list():
    try:
        journal_type = PublicationType.objects.get(name__icontains='conference')
        # print(journal_type)
    except:
        print('Failed to get journal publication type')
        return [], []

    articles = Publication.objects.filter(publication_type=journal_type, wos_citation_count__gt=0, scopus_citation_count__gt=0)
    
    result = []
    
    for article in articles:   
        meta = {}

        # citations
        cit = []
        if article.wos_citation_count and article.wos_citation_count>0:
            cit.append(f'{article.wos_citation_count} (WoS)')
        if article.scopus_citation_count and article.scopus_citation_count>0:
            cit.append(f'{article.scopus_citation_count} (Scopus)')
        meta['citations'] = ', '.join(cit)

        result.append((article, meta))

    return result

