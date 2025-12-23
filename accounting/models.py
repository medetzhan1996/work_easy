from decimal import Decimal

from django.db import models
from django.conf import settings
from django.db.models import Sum, IntegerField, F, Value, Q, FloatField, DecimalField
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from account.models import Company


class ItemBase(models.Model):
    title = models.CharField(max_length=180, verbose_name='Наименование')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Contractor(ItemBase):
    """ Контрагент """

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'


class TransactionQueryset(QuerySet):

    def accounting(self):
        """Accounting for Transactions"""
        return self.annotate(
            commission=Coalesce('transaction_details__commission', Value(0), output_field=FloatField()),
            purchase_material_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.PURCHASE_MATERIAL)), Value(0),
                output_field=IntegerField()),
            staff_salary_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.STAFF_SALARY)), Value(0),
                output_field=IntegerField()),
            taxes_fees_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.TAXES_FEES)), Value(0),
                output_field=IntegerField()),
            sale_good_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.SALE_GOOD)), Value(0),
                output_field=IntegerField()),
            transfer_replenishment_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.TRANSFER_REPLENISHMENT)), Value(0),
                output_field=IntegerField()),
            transfer_write_off_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.TRANSFER_WRITE_OFF)), Value(0),
                output_field=IntegerField()),
            other_income_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.OTHER_INCOME)), Value(0),
                output_field=IntegerField()),
            other_expenses_sum=Coalesce(
                Sum('transaction_details__price',
                    filter=Q(operation_method=Transaction.OTHER_EXPENSES)), Value(0),
                output_field=IntegerField()),
        ).annotate(
            total_sum=Coalesce(
                (F('sale_good_sum') - (F('sale_good_sum') * F('commission') / 100)) -
                F('staff_salary_sum') - F('taxes_fees_sum') -
                F('purchase_material_sum') + F('other_income_sum') - F('other_expenses_sum') +
                F('transfer_replenishment_sum') - F('transfer_write_off_sum'),

                Value(0), output_field=IntegerField())
        )

    def get_income_for_employees(self, users, start_date, end_date):
        """
        Получить доход для списка работников за указанный месяц.

        :param users: Список объектов пользователей (работников)
        :param start_date: Дата начала
        :param end_date: Дата конца
        :return: Словарь, где ключ - ID работника, значение - его доход за месяц.
        """
        # Получите QuerySet транзакций для этого списка пользователей и месяца
        transactions = self.filter(
            user__in=users,
            created_at__range=(start_date, end_date),
            operation_method__in=[Transaction.SALE_GOOD, Transaction.OTHER_INCOME]
        ).annotate(
            annotated_user_id=F('user__id')
        ).values(
            'annotated_user_id'
        ).annotate(
            total_income=Coalesce(Sum('transaction_details__price'), Decimal('0.00'), output_field=DecimalField())
        )

        # Преобразуйте результат в словарь
        income_dict = {item['annotated_user_id']: item['total_income'] for item in transactions}

        return income_dict

    def mark_as_write_off(self, content_type, object_id, description, user):
        return self.create(
            content_type=content_type,
            operation_method=Transaction.TRANSFER_WRITE_OFF,
            object_id=object_id, user=user,
            description=description
        )

    def mark_as_replenishment(self, content_type, object_id, description, user):
        return self.create(
            content_type=content_type,
            operation_method=Transaction.TRANSFER_REPLENISHMENT,
            object_id=object_id, user=user,
            description=description
        )

    def for_payment_method(self, payment_method):
        return self.filter(transaction_details__payment_method=payment_method).accounting()

    def for_payment_methods(self, payment_methods):
        return self.filter(transaction_details__payment_method__in=payment_methods).accounting()


class Transaction(models.Model):
    """ Транзакции """
    PURCHASE_MATERIAL = "PURCHASE_MATERIAL"
    STAFF_SALARY = "STAFF_SALARY"
    TAXES_FEES = "TAXES_FEES"
    SALE_GOOD = "SALE_GOOD"
    OTHER_INCOME = "OTHER_INCOME"
    OTHER_EXPENSES = "OTHER_EXPENSES"
    TRANSFER_REPLENISHMENT = "TRANSFER_REPLENISHMENT"
    TRANSFER_WRITE_OFF = "TRANSFER_WRITE_OFF"
    PREPAID_EXPENSE = "PREPAID_EXPENSE"
    DELIVERY_CONSUMPTION = "DELIVERY_CONSUMPTION"
    OperationMethod = (
        (PURCHASE_MATERIAL, "Закупка материалов"),
        (STAFF_SALARY, "Зарплата персонала"),
        (TAXES_FEES, "Налоги и сборы"),
        (SALE_GOOD, "Продажа товара"),
        (DELIVERY_CONSUMPTION, "Расходы доставки"),
        (OTHER_EXPENSES, "Прочие расходы"),
        (OTHER_INCOME, "Прочие доходы"),
        (TRANSFER_REPLENISHMENT, "Перевод пополнение"),
        (TRANSFER_WRITE_OFF, "Перевод списание"),
        (PREPAID_EXPENSE, "Аванс"),
    )

    operation_method = models.CharField(
        max_length=30, choices=OperationMethod, verbose_name='Вид операции')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('user', 'contractor', 'customer', 'order', 'transactionmove', 'salary')},
        null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    item = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TransactionQueryset.as_manager()

    def get_update_url(self):
        return 'accounting:transaction_update'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'operation_method'],
                name='unique_item'
            )
        ]

    def mark_as_sale_good(self, commit: bool = False):
        self.operation_method = self.SALE_GOOD
        if commit:
            self.save()

    @property
    def price(self):
        """Рассчитайте общую стоимость всех деталей транзакции."""
        return self.transaction_details.aggregate(Sum('price'))['price__sum'] or 0


class PaymentMethodQueryset(QuerySet):

    def for_company(self, company):
        return self.filter(company=company)


class PaymentMethod(ItemBase):
    bank = models.ForeignKey('self', on_delete=models.PROTECT, verbose_name='Банк', null=True, blank=True)
    commission = models.FloatField()
    objects = PaymentMethodQueryset.as_manager()

    def __str__(self):
        return f"{self.bank.title if self.bank else ''} {self.title}".strip()

    @classmethod
    def get_payment_method(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist as e:
            raise cls.DoesNotExist(f"PaymentMethod with pk '{pk}' does not exist") from e

    def get_child_payment_methods(self):
        child_ids = list(self.paymentmethod_set.all().values_list('id', flat=True))
        return [self.id] + child_ids

    @staticmethod
    def get_grouped_choices():
        grouped_choices = []
        parent_methods = PaymentMethod.objects.filter(bank__isnull=True)

        for parent in parent_methods:
            child_methods = parent.paymentmethod_set.all()
            group = (str(parent), [(child.id, str(child)) for child in child_methods])
            grouped_choices.append(group)

        return grouped_choices


class PaymentMethodCommissionQueryset(QuerySet):

    def latest_before_date(self, specified_date):
        return self.filter(date__lte=specified_date).order_by('-date')

    def for_payment_method(self, payment_method):
        return self.filter(payment_method=payment_method)


class PaymentMethodCommission(models.Model):
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    commission = models.FloatField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')
    date = models.DateField()
    objects = PaymentMethodCommissionQueryset.as_manager()

    def __str__(self):
        return "{} / {} / {} / {} %".format(
            self.payment_method.title, self.date, self.company.title, self.commission)


class TransactionDetail(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, verbose_name='Транзакция',
                                    related_name='transaction_details')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name='Способ оплаты')
    commission = models.FloatField(null=True, blank=True, verbose_name='Комиссия')
    price = models.DecimalField(max_digits=19, decimal_places=0)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('formfield',)},
        blank=True, null=True,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    item = GenericForeignKey('content_type', 'object_id')


class TransactionMove(models.Model):
    payment_method_from = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE,
                                            verbose_name='Из кассы', related_name="tm_payment_methods_from")
    payment_method_to = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE,
                                          verbose_name='В кассу', related_name="tm_payment_methods_to")
    price = models.DecimalField(max_digits=19, decimal_places=0)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')




