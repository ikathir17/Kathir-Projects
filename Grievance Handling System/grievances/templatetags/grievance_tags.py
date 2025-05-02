from django import template

register = template.Library()

@register.filter
def status_count(queryset, statuses):
    status_list = [s.strip() for s in statuses.split(',')]
    return queryset.filter(status__in=status_list).count()