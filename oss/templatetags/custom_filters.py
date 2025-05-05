from django import template

register = template.Library()

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    return dictionary.get(key)

@register.filter
def display_recommendation(value):
    recommendations = {
        'A': 'Accept',
        'R': 'Reject',
        'MIN_R': 'Minor Revision',
        'MAJ_R': 'Major Revision',
    }
    return recommendations.get(value, '')

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def startswith(value, arg):
    return value.startswith(arg)