from django.contrib.contenttypes.models import ContentType


def combine_queryset_data(data):
    result = []
    for value in data:
        content_type = ContentType.objects.get_for_model(type(value)).id
        uuid = str(value.id) + '_' + str(content_type)
        result.append({
            'id': uuid,
            'title': value.title,
            'content_type': content_type
        })
    return result
