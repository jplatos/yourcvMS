from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def latex_escape(value):
    return value.replace('&', '\&').replace('_', '\\_')
