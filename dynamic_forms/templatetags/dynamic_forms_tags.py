import json
from datetime import date

from django.core.cache import cache
from django import template

from accounting.models import PaymentMethodCommission
from products.models import Product, Material

register = template.Library()

@register.simple_tag
def get_item(value, key):
    if value is None or key is None:
        return ''
    if value and key:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return ''
        # If the value is a dictionary, get the item
        if isinstance(value, dict):
            return value.get(key) or ''
    return ''


@register.simple_tag
def check_blocking_field(value, key):
    blocking_field_value = get_item(value, key)
    if blocking_field_value or blocking_field_value == 'true':
        return True
    return False


@register.simple_tag
def is_selected(value1, value2):
    if str(value1) == str(value2):
        return 'selected'
    return ''


@register.simple_tag
def universal_filter(queryset, **kwargs):
    return queryset.filter(**kwargs)


@register.simple_tag
def from_json(value):
    if value:
        return json.loads(value)
    else:
        return {'id': '', 'label': '............'}


@register.inclusion_tag('dynamic_forms/tags/material_by_category.html', takes_context=True)
def material_by_category(context, form_field, form_field_val=''):
    user = context['request'].user
    category = form_field.associated_object_id
    form_field_val = int(form_field_val) if form_field_val else ''
    """
    Извлекает материалы для данной категории
    """
    # Cache materials
    cache_key = f'materials_for_category_{category}'
    materials = cache.get(cache_key)
    if materials is None:

        try:
            materials = Material.objects.filter(category__company=user.company).for_category(category)
            # Кэш результатов на 5 минут (300 секунд)
            cache.set(cache_key, materials, 60)
        except Exception as e:
            # Зарегистрировать или обработать исключение
            materials = Material.objects.none()
    return {'materials': materials, 'form_field': form_field, 'form_field_val': form_field_val}


@register.inclusion_tag('dynamic_forms/tags/product.html', takes_context=True)
def product(context, form_field, form_field_val=''):
    user = context['request'].user
    form_field_val = int(form_field_val) if form_field_val else ''
    """
    Извлекает материалы для данной категории
    """
    # Cache materials
    cache_key = 'product'
    products = Product.objects.all()
    return {'products': products, 'form_field': form_field, 'form_field_val': form_field_val}


@register.simple_tag
def calculate_price_after_commission(field, serialized_data, specified_date):
    payment_method_commission = PaymentMethodCommission.objects.latest_before_date(specified_date)
    price = field.calculate_price_after_commission(payment_method_commission, serialized_data)
    return int(price) if price else '.........'


@register.simple_tag
def get_total_receipt_amount(order):
    specified_date = date(2023, 7, 12)
    payment_method_commission = PaymentMethodCommission.objects.latest_before_date(specified_date)
    return order.total_receipt_amount(payment_method_commission)


