from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
def publication_type(queryset, pubtype):
    return queryset.filter(publication_type=pubtype)
