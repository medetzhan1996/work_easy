from django import template

register = template.Library()


@register.simple_tag
def custom_cycle(value):
    colors = ['border-left-green', 'border-left-blue', 'border-left-yellow']
    return colors[value % 3]
