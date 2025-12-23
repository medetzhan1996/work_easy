from django import template

from account.models import User

register = template.Library()


@register.inclusion_tag('account/includes/user_dropdown.html')
def user_dropdown(name, user):
    users = User.objects.filter(company=user.company).all()
    return {'users': users, 'name': name}