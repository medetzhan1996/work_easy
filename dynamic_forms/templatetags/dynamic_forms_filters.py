import json

from django import template
from datetime import datetime
from django.utils import timezone

register = template.Library()


@register.filter
def get_item(value, key):
    if value is None or key is None:
        return ""
    if value and key:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return ""
        # If the value is a dictionary, get the item
        if isinstance(value, dict):
            return value.get(key) or ""
    return ""


@register.filter
def check_blocking_field(value, field):
    if field:
        blocking_field_value = get_item(value, field.name)
        if blocking_field_value or blocking_field_value == "true":
            return True
    return False


@register.filter
def format_date(value, format_string):
    try:
        date_object = datetime.strptime(value, "%Y-%m-%d")
        return date_object.strftime(format_string)
    except ValueError:
        return ""


@register.filter
def is_checked(value, key):
    item = get_item(value, key)
    if isinstance(item, str):
        item = item.lower()
        if item == "false":
            return False
        elif item == "true":
            return True
    return bool(item)


@register.filter(name="get_form_field")
def get_form_field(form, field_name):
    return form[field_name]


@register.filter
def has_full_permission(field, user_type):
    return field.has_full_permission(user_type)


@register.filter
def is_selected(payment_method_id, form_field_val):
    return "selected" if payment_method_id == form_field_val else ""
