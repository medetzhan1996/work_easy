import json
from datetime import datetime
from decimal import Decimal

from django.db.models import (
    Max,
    ExpressionWrapper,
    Sum,
    Case,
    When,
    F,
    Value,
    DecimalField,
    OuterRef,
    Subquery,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.db.models import F, Sum, JSONField
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from accounting.models import PaymentMethodCommission, TransactionDetail
from constants import (
    SURCHARGE,
    ACCEPTING_PAYMENT,
    DISCOUNT,
    DISCOUNT_PERCENT,
    PAYMENT_AFTER_COMMISSION,
    RECEIPT_AMOUNT,
)
from customers.models import Customer
from dynamic_forms.models import FormField
from products.models import Product


class OrderQueryset(QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def for_company(self, company):
        return self.filter(user__company=company)

    def total_receipt_amount_for_user(self, user):
        return (
            self.for_user(user).aggregate(total=Sum("total_receipt_amount"))["total"]
            or 0
        )

    def _get_paid_per_order(self):
        order_content_type = ContentType.objects.get_for_model(self.model)

        return (
            TransactionDetail.objects.filter(
                transaction__content_type=order_content_type,
                transaction__object_id=OuterRef("id"),
            )
            .annotate(
                net_paid=ExpressionWrapper(
                    F("price") - (F("price") * F("commission") / 100),
                    output_field=DecimalField(max_digits=19, decimal_places=2),
                )
            )
            .values("net_paid")
            .annotate(total_paid=Sum("net_paid"))
            .values("total_paid")
        )

    def _bonus_calculation(self, paid_per_order):
        return Case(
            When(
                product__bonus__bonus_type="fixed",
                then=F("product__bonus__bonus_value"),
            ),
            When(
                product__productbonus__bonus_type="percentage",
                then=ExpressionWrapper(
                    Subquery(paid_per_order)
                    * F("product__productbonus__bonus_value")
                    / 100,
                    output_field=DecimalField(max_digits=19, decimal_places=2),
                ),
            ),
            default=Value(0),
            output_field=DecimalField(max_digits=19, decimal_places=2),
        )

    def bonuses_per_user(self):
        paid_per_order = self._get_paid_per_order()
        bonus_calc = self._bonus_calculation(paid_per_order)

        return (
            self.annotate(bonus=bonus_calc)
            .values("user__username")
            .annotate(total_bonus=Sum("bonus"))
            .order_by("user__username")
        )


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, null=True, blank=True
    )
    salesman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_salesmans",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=19, decimal_places=0)
    deadline = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_makers",
        null=True,
        blank=True,
    )
    total_receipt_amount = models.DecimalField(
        max_digits=19, decimal_places=0, default=0
    )
    extra_data = JSONField(default=dict, null=True, blank=True)
    create_date = models.DateField(auto_now_add=True)
    unicode = models.CharField(max_length=19)
    day_index = models.IntegerField(default=1)
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    item = GenericForeignKey("content_type", "object_id")
    objects = OrderQueryset.as_manager()

    def save(self, *args, **kwargs):
        create_date = datetime.now().date()
        if not self.pk:
            # Получаем количество заказов, сделанных пользователем в этот день
            max_index = Order.objects.filter(
                user=self.user, create_date=create_date
            ).aggregate(Max("day_index"))["day_index__max"]
            self.day_index = (max_index or 0) + 1
            self.unicode = (
                f"{create_date.strftime('%d/%m/%Y')}/{self.user.id}/{self.day_index}"
            )
        payment_method_commission = PaymentMethodCommission.objects.latest_before_date(
            create_date
        )
        self.total_receipt_amount = self._calculate_total_receipt_amount(
            payment_method_commission
        )
        super().save(*args, **kwargs)

    def _sum_extra_data(self, field_type):
        form_field_names = FormField.objects.filter(field_type=field_type).values_list(
            "name", flat=True
        )
        total_sum = Decimal(0)
        extra_data = json.loads(self.extra_data)
        for field_name in form_field_names:
            field_value = extra_data.get(field_name)
            if field_value and field_value is not None:
                total_sum += Decimal(field_value)
        return total_sum

    @property
    def total_payment(self):
        """
        Вычислить общую сумму к оплате
        """
        return Decimal(self.discount_payment) + self._sum_extra_data(SURCHARGE)

    def _calculate_total_receipt_amount(self, payment_method_commission):
        """
        Вычислить общую сумму к получению
        """
        form_fields = FormField.objects.filter(
            field_type=PAYMENT_AFTER_COMMISSION
        ).all()
        total_sum = Decimal(0)
        for form_field in form_fields:
            price = form_field.calculate_price_after_commission(
                payment_method_commission, self.extra_data
            )
            if price:
                total_sum += Decimal(price)
        return total_sum

    @property
    def discount_payment(self):
        """
        Вычислить сумму к оплате со скидкой
        """
        discount = Decimal(self._sum_extra_data(DISCOUNT))
        price = Decimal(self.price)
        if discount:
            discounted_price = price * (Decimal(1) - discount * DISCOUNT_PERCENT)
            return discounted_price.quantize(Decimal("1"))  # Округление до целого числа
        return price.quantize(Decimal("1"))  # Округление до целого числа

    @property
    def total_paid(self):
        """
        Вычислить общую оплаченную сумму
        """
        return self._sum_extra_data(ACCEPTING_PAYMENT)

    @property
    def remainder(self):
        """
        Вычислить остаток оплачеваемой суммы
        """
        return self.total_payment - self.total_paid

    def get_total_price(self):
        """
        Вычислить общую стоимость заказа на основе связанных экземпляров OrderProduct.
        Возвращает 0, если нет связанных экземпляров OrderProduct.
        """
        if self.orderproduct_set.exists():
            return self.orderproduct_set.aggregate(
                total_price=Sum(
                    F("count") * F("price"), output_field=models.DecimalField()
                )
            )["total_price"]
        else:
            return 0


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
