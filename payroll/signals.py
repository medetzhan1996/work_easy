from django.db.models.signals import post_save
from django.dispatch import receiver

from accounting.models import Transaction
from .models import Salary


@receiver(post_save, sender=Transaction)
def update_salary(sender, instance, **kwargs):
    if instance.operation_method == Transaction.STAFF_SALARY and instance.item and isinstance(instance.item, Salary):
        salary = instance.item
        salary.is_full_payment = True
        salary.save()
