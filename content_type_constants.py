from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from account.models import User


def get_content_type_for_model(model, cache_key, timeout=3600):
    ct = cache.get(cache_key)
    if not ct:
        ct = ContentType.objects.get_for_model(model)
        cache.set(cache_key, ct, timeout=timeout)
    return ct


MATERIAL_CT_CACHE_KEY = 'material_ct'
CARD_CT_CACHE_KEY = 'card_ct'
SALARY_CT_CACHE_KEY = 'salary_ct'
PRODUCT_CT_CACHE_KEY = 'product_ct'
TRANSACTION_CT_CACHE_KEY = 'transaction_ct'
TRANSACTION_MOVE_CT_CACHE_KEY = 'transaction_move_ct'
CUSTOMER_CT_CACHE_KEY = 'customer_ct'
ORDER_CT_CACHE_KEY = 'order_ct'
ORDER_PRODUCT_CT_CACHE_KEY = 'order_product_ct'
FORM_FIELD_CT_CACHE_KEY = 'form_field_ct'
USER_CT_CACHE_KEY = 'user_ct'
DEPARTMENT_CT_CACHE_KEY = 'department_ct'

OPERATION_METHOD_CONTENT_TYPE_MAP = {
    'PREPAID_EXPENSE': USER_CT_CACHE_KEY,
    'STAFF_SALARY': USER_CT_CACHE_KEY,
}

OPERATION_METHOD_MODEL_MAP = {
    'PREPAID_EXPENSE': User,
    'STAFF_SALARY': User,
}
