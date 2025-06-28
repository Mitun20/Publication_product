from django import template

register = template.Library()

@register.filter
def reverse_queryset(value):
    """Reverses the order of a queryset."""
    return value[::-1] if value else value

@register.filter
def range_max_star(value):
    return range(value)