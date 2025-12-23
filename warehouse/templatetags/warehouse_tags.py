from django import template
from warehouse.utils import get_object_by_content_type_and_id

register = template.Library()


@register.simple_tag
def get_object_by_content_type(content_type_id, object_id):
    if content_type_id and object_id:
        return get_object_by_content_type_and_id(content_type_id, object_id)
    return None
