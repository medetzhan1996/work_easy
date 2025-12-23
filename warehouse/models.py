from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Sum, IntegerField, F, Value, Q, FloatField
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.conf import settings

from account.models import Company
from products.models import Product, Material


class ItemBase(models.Model):
    title = models.CharField(max_length=180, verbose_name='Наименование')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Storage(ItemBase):
    """ Склад """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Contractor(ItemBase):
    """ Контрагент """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания',
                                related_name='warehouse_contractors')

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'


class StorageOperationQueryset(QuerySet):

    def accounting(self):
        """Accounting for Transactions"""
        return self.annotate(
            coming_sum=Coalesce(
                Sum('storage_operation_details__quantity',
                    filter=Q(operation_method=StorageOperation.COMING)), Value(0),
                output_field=IntegerField()),
            write_off_sum=Coalesce(
                Sum('storage_operation_details__quantity',
                    filter=Q(operation_method=StorageOperation.WRITE_OFF)), Value(0),
                output_field=IntegerField()),
            moving_replenishment=Coalesce(
                Sum('storage_operation_details__quantity',
                    filter=Q(operation_method=StorageOperation.MOVING_REPLENISHMENT)), Value(0),
                output_field=IntegerField()),
            moving_write_off_sum=Coalesce(
                Sum('storage_operation_details__quantity',
                    filter=Q(operation_method=StorageOperation.MOVING_WRITE_OFF)), Value(0),
                output_field=IntegerField()),
        ).annotate(
            total_sum=Coalesce(
                F('coming_sum') - F('write_off_sum') +
                F('moving_replenishment') - F('moving_write_off_sum'),
                Value(0), output_field=IntegerField())
        )


class StorageOperation(models.Model):
    """ Складские операции """
    COMING = "COMING"
    WRITE_OFF = "WRITE_OFF"
    MOVING_REPLENISHMENT = "MOVING_REPLENISHMENT"
    MOVING_WRITE_OFF = "MOVING_WRITE_OFF"

    OperationMethod = (
        (COMING, 'Приход'),
        (WRITE_OFF, 'Списание'),
        (MOVING_REPLENISHMENT, "Перемещение пополнение"),
        (MOVING_WRITE_OFF, "Перемещение списание"),
    )

    operation_method = models.CharField(
        max_length=30, choices=OperationMethod, verbose_name='Вид операции')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('user', 'contractor', )},
        null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    item = GenericForeignKey('content_type', 'object_id')
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = StorageOperationQueryset.as_manager()


class StorageOperationDetail(models.Model):
    storage_operation = models.ForeignKey(StorageOperation, on_delete=models.CASCADE,
                                          related_name='storage_operation_details')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('material', 'product')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    quantity = models.FloatField(default=1)


class StorageOperationMove(models.Model):
    storage_from = models.ForeignKey(Storage, on_delete=models.CASCADE,
                                     verbose_name='Из склада', related_name="sm_storage_from")
    storage_to = models.ForeignKey(Storage, on_delete=models.CASCADE,
                                   verbose_name='В склад', related_name="sm_storage_to")
    quantity = models.FloatField(default=1)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')


class Consumable(models.Model):
    """ Расходные материалы """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    consumption = models.FloatField(default=0)