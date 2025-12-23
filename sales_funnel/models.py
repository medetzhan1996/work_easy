from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet

from account.models import Company
from customers.models import Customer


class Funnel(models.Model):
    """ Воронка """
    title = models.CharField(max_length=320)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sorting = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class CardQueryset(QuerySet):
    def for_user(self, user):
        return self.filter(user=user)


class Card(models.Model):
    """ Карточки варонки """
    funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = CardQueryset.as_manager()

