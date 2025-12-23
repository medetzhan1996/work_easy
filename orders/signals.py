import json
import decimal


from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from content_type_constants import get_content_type_for_model, ORDER_CT_CACHE_KEY, FORM_FIELD_CT_CACHE_KEY
from constants import PAYMENT_CONFIRMATION, DELIVERY_CONSUMPTION
from dynamic_forms.models import FormField
from accounting.models import PaymentMethod, Transaction, TransactionDetail
from orders.models import Order


@transaction.atomic
@receiver(post_save, sender=Order)
def order_payment_handler(sender, instance, created, **kwargs):
    order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
    payment_transaction, created = Transaction.objects.get_or_create(
        content_type=order_ct, object_id=instance.id,
        operation_method=Transaction.SALE_GOOD,
        defaults={'user': instance.user},
    )
    try:
        extra_data = json.loads(instance.extra_data)
    except json.JSONDecodeError as e:
        return
    form_field_ct = get_content_type_for_model(FormField, FORM_FIELD_CT_CACHE_KEY)
    payment_confirmation_form_fields = FormField.objects.filter(
        name__in=extra_data, field_type=PAYMENT_CONFIRMATION)
    for payment_confirmation_form_field in payment_confirmation_form_fields:
        price_field = payment_confirmation_form_field.associated_field
        payment_method_field = price_field.associated_field
        payment_method_id, price = payment_confirmation_form_field.get_confirmation_payment_fields(
            price_field, payment_method_field, extra_data)
        if payment_method_id and price:
            price = decimal.Decimal(price)
            payment_method = PaymentMethod.get_payment_method(int(payment_method_id))
            transaction_detail_exists = TransactionDetail.objects.filter(
                content_type=form_field_ct,
                object_id=payment_confirmation_form_field.id,
                transaction=payment_transaction,
                payment_method=payment_method).exists()
            if not transaction_detail_exists:
                TransactionDetail.objects.create(
                    item=payment_confirmation_form_field,
                    payment_method=payment_method,
                    price=price,
                    transaction=payment_transaction,
                    commission=payment_method.commission
                )
    delivery_consumption_form_fields = FormField.objects.filter(
        name__in=extra_data, field_type=DELIVERY_CONSUMPTION)
    if delivery_consumption_form_fields.exists():
        payment_transaction, created = Transaction.objects.get_or_create(
            content_type=order_ct, object_id=instance.id,
            operation_method=Transaction.DELIVERY_CONSUMPTION,
            defaults={'user': instance.user},
        )
        for delivery_consumption_form_field in delivery_consumption_form_fields.all():
            price_field = delivery_consumption_form_field
            payment_method_field = price_field.associated_field
            if price_field and payment_method_field:
                payment_method_id, price = delivery_consumption_form_field.get_confirmation_payment_fields(
                    price_field, payment_method_field, extra_data)

                if payment_method_id and price:
                    price = decimal.Decimal(price)
                    payment_method = PaymentMethod.get_payment_method(int(payment_method_id))
                    transaction_detail_exists = TransactionDetail.objects.filter(
                        content_type=form_field_ct,
                        object_id=delivery_consumption_form_field.id,
                        transaction=payment_transaction,
                        payment_method=payment_method).exists()
                    if not transaction_detail_exists:
                        TransactionDetail.objects.create(
                            item=delivery_consumption_form_field,
                            payment_method=payment_method,
                            price=price,
                            transaction=payment_transaction,
                            commission=0
                        )


