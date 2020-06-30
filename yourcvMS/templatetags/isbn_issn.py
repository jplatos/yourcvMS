from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def issn(value):
    if value and len(value)==8:
        return f'{value[:4]}-{value[4:]}'
    else: 
        return value
