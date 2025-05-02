from django import template
from ..models import Grievance

register = template.Library()

@register.filter(name='status_count')
def status_count(queryset, statuses):
    status_list = [s.strip() for s in statuses.split(',')]
    return queryset.filter(status__in=status_list).count()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)