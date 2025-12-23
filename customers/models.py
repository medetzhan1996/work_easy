from django.db import models
from django.db.models.query import QuerySet

from account.models import Company


class CustomerQueryset(QuerySet):

    def search(self, query):
        return self.filter(full_name__icontains=query).all()


class Customer(models.Model):
    """ Список клиентов """
    full_name = models.CharField(max_length=320, null=True, blank=True)
    phone_number = models.CharField(max_length=180)
    social_account = models.CharField(max_length=180, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    objects = CustomerQueryset.as_manager()

    def __str__(self):
        return self.phone_number
