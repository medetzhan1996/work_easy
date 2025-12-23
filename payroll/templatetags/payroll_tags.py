from django import template
from decimal import Decimal

register = template.Library()


@register.simple_tag
def get_value_from_dict(data_dict, key, default_value=0):
    """
    Возвращает значение из словаря по указанному ключу.
    """
    return data_dict.get(key, default_value)


@register.simple_tag
def calculate_amount(initial_amount, percentage):
    percentage_decimal = Decimal(percentage) / 100
    result = initial_amount * percentage_decimal
    return result.quantize(Decimal('1'))


@register.simple_tag
def get_users_by_payment(users, salary_type):
    return users.filter(salarysetup__salary_type=salary_type)
