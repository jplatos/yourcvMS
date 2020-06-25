from titlecase import titlecase

def titlelize(title):
    return titlecase(title)

def normalize_isbn(isbn):
    return isbn.replace('-', '')

def normalize_issn(issn):
    return issn.replace('-', '')