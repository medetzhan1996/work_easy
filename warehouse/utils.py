from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404


def get_object_by_content_type_and_id(content_type_id, object_id):
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    obj = get_object_or_404(model_class, id=object_id)
    return obj
