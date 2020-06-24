import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogenize_latex_encoding, convert_to_unicode

with open('wos_2020-05-16.bib') as bibtex_file:
    parser = BibTexParser()
    parser.customization = homogenize_latex_encoding
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.load(bibtex_file)

print(bib_database.entries[0].keys())

