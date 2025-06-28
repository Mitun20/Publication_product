from django import template

register = template.Library()

@register.filter
def range_max_star(value):
    return range(value)