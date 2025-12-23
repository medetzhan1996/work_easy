import json
import logging

from django.core.exceptions import ValidationError

# Get an instance of a logger
logger = logging.getLogger(__name__)


def check_field_exists(field):
    if not field:
        error_message = f'{field.name} is not set.'
        logger.error(error_message)
        return None
    return field


def get_deserialized_value(serialized_data, field, error_message):
    deserialized_value = serialized_data.get(field)
    if deserialized_value is None:
        logger.error(error_message)
        raise ValidationError(error_message)
    return deserialized_value


def deserialize_json(serialized_data):
    try:
        deserialized_data = json.loads(serialized_data)
        return deserialized_data
    except json.JSONDecodeError:
        return None
