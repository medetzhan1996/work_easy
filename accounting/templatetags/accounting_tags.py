from django.db.models import Sum
from django import template

from account.models import User
from accounting.models import Transaction

register = template.Library()


@register.simple_tag
def get_payment_method_sum(pk):
    payment_method_sum = Transaction.objects.for_payment_method(pk).aggregate(
        total=Sum('total_sum')
    )['total']
    return payment_method_sum or 0


@register.simple_tag
def get_payment_methods_sum(payment_methods):
    payment_methods_sum = Transaction.objects.for_payment_methods(payment_methods).aggregate(
        total=Sum('total_sum')
    )['total']
    return payment_methods_sum or 0


@register.filter
def class_name(value):
    return value.__class__.__name__.lower()
