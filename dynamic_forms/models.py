import json

from django.db import models
from django.db.models import JSONField
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.contrib.contenttypes.fields import GenericForeignKey

from account.models import Company
from constants import USER_TYPE_CHOICES, FIELD_TYPE_CHOICES, PERMISSION_CHOICES, FULL, ACCEPTING_PAYMENT
from .utils import check_field_exists, deserialize_json


class FormFieldQueryset(QuerySet):

    def filter_content_type(self, model):
        query = self.filter(content_type=ContentType.objects.get_for_model(model))
        return query

    def for_company(self, company):
        return self.filter(company=company)

    def get_payment_fields(self, content_type):
        query = self.filter(content_type=content_type, field_type=ACCEPTING_PAYMENT)
        return query

    def get_form_data(self, content_type):
        data = self.filter(content_type=content_type).values_list('name', 'label')
        return [{'name': k, 'label': v, 'initial': ''} for k, v in data]


class FormField(models.Model):
    label = models.CharField(max_length=320)
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=100, choices=FIELD_TYPE_CHOICES)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('card', 'order', 'orderproduct')})
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    choices = JSONField(default=dict, null=True, blank=True)
    is_required = models.BooleanField(default=False)
    associated_content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL,
                                                related_name='associated_content_type_by')
    associated_object_id = models.PositiveIntegerField(null=True, blank=True)
    associated_field = GenericForeignKey('associated_content_type', 'associated_object_id')
    associated_blocking_field = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                                  related_name='blocked_by')
    color = models.CharField(max_length=15, null=True, blank=True)
    styles = models.CharField(max_length=320, null=True, blank=True)
    sorting = models.PositiveIntegerField(default=0)
    is_select2 = models.BooleanField(default=False)
    classes = models.CharField(max_length=320, null=True, blank=True)
    objects = FormFieldQueryset.as_manager()

    @property
    def associated_required_fields_as_list(self):
        return [associated_required_field.name for associated_required_field in self.associated_required_fields.all()]

    def calculate_price_after_commission(self, payment_method_commission, serialized_data):
        price_field = self.associated_field
        payment_method_field = price_field.associated_field
        deserialized_data = deserialize_json(serialized_data)
        payment_method, price = self.get_confirmation_payment_fields(
            price_field, payment_method_field, deserialized_data)
        if payment_method and price:
            payment_method_commission_obj = payment_method_commission.for_payment_method(payment_method).first()
            if payment_method_commission_obj:
                commission = float(payment_method_commission_obj.commission)
                result = price - (price * commission / 100)
                return result
        return None

    def get_confirmation_payment_fields(self, price_field, payment_method_field, data):
        price_val = data.get(price_field.name, 0)
        payment_method_val = data.get(payment_method_field.name, '{}')
        price = float(price_val) if price_val else 0
        deserialized_payment_method = deserialize_json(payment_method_val) if payment_method_val else {}
        payment_method = deserialized_payment_method.get('id')
        if payment_method and price:
            return payment_method, price
        return None, None


    @staticmethod
    def get_total_sum(form_fields, form_data, field_type):
        """
        Возвращает сумму всех значений в form_data, чей соответствующий FormField
        имеет field_type, который соответствует предоставленному field_type.
        """
        field_names = form_fields.filter(field_type=field_type).values_list('name', flat=True)
        return sum(form_data.get(name, 0) or 0 for name in field_names)

    def has_full_permission(self, user_type):
        return self.formfieldpermission_set.filter(user_type=user_type, permission=FULL).exists()

    class Meta:
        unique_together = ('name', 'company')

    def __str__(self):
        return "{} / {}".format(self.label, self.name)


class FormFieldPermission(models.Model):
    form_field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default=FULL)
    sorting = models.IntegerField(default=0)

    class Meta:
        ordering = ['sorting']


class DynamicFormQueryset(QuerySet):

    def filter_content_type(self, model):
        query = self.filter(content_type=ContentType.objects.get_for_model(model))
        return query

    def get_dynamic_form_data(self, model, object_id=None):
        dynamic_form_data = self.filter_content_type(model)
        if object_id:
            dynamic_form_data = dynamic_form_data.filter(object_id=object_id)
        data = dynamic_form_data.values_list('field_name', 'field_value')
        return dict((k, v) for k, v in data)


class DynamicFormData(models.Model):
    field_name = models.CharField(max_length=320)
    field_value = models.CharField(max_length=320)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('card', 'order', 'orderproduct')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    objects = DynamicFormQueryset.as_manager()

    @classmethod
    def create_dynamic_form_data(cls, obj, additional_form_data):
        content_type = ContentType.objects.get_for_model(obj)
        dynamic_form_data = []
        for name, value in additional_form_data.items():
            dynamic_form_instance, created = cls.objects.update_or_create(
                field_name=name, content_type=content_type, object_id=obj.id,
                defaults={'field_value': value}
            )
            dynamic_form_data.append(dynamic_form_instance)
        return dynamic_form_data