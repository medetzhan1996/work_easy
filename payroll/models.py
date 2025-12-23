from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models import ExpressionWrapper
from django.conf import settings
from django.db.models import Sum, Case, When, F, Value, DecimalField, OuterRef, Subquery
from django.contrib.contenttypes.models import ContentType

from accounting.models import TransactionDetail
from constants import SALARY_TYPE_CHOICES, SALARY_PERCENTAGE_PREMIUM, SALARY_FIXED_PREMIUM, BONUS_TYPE_CHOICES
from orders.models import Order
from products.models import Product


class PenaltyManager(models.Manager):

    def get_total_penalty_by_users(self, users, year, month):
        # Получить все штрафы за указанный месяц и год для заданных пользователей
        penalties = self.filter(date__year=year, date__month=month, user__in=users)
        # Сгруппировать штрафы по пользователям и просуммировать их
        total_penalties_by_users = penalties.values('user').annotate(
            total_penalty=Sum('penalty')).order_by('user')

        # Преобразовать результат в словарь, где ключ - ID пользователя, а значение - общая сумма штрафов
        return {item['user']: item['total_penalty'] for item in total_penalties_by_users}


class Penalty(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    penalty = models.DecimalField(max_digits=19, decimal_places=0)
    comment = models.TextField()
    objects = PenaltyManager()


class SalarySetup(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=19, decimal_places=0)
    salary_type = models.CharField(max_length=80, choices=SALARY_TYPE_CHOICES)
    premium = models.FloatField()

    @property
    def total_premium(self):
        if self.salary_type == SALARY_PERCENTAGE_PREMIUM:
            return self.premium
        else:
            return (self.premium / 100) * self.salary


class SalaryManager(models.Manager):

    def users_without_salary_records(self, year, month):
        existing_salaries = self.filter(month_year__year=year, month_year__month=month)
        return set(existing_salaries.values_list('user_id', flat=True))

    def create_or_update_salaries_for_users(self, users, year, month, salary_data):
        # Convert to date once
        target_month_year = date(year, month, 1)

        # Filter out users with is_full_payment=True for the month_year
        fully_paid_users = set(
            Salary.objects.filter(month_year=target_month_year, is_full_payment=True).values_list('user', flat=True)
        )
        eligible_users = [user for user in users if user.id not in fully_paid_users]

        for user in eligible_users:
            defaults = {
                'completed_amount': salary_data.get('income_for_employees', {}).get(user.id, 0),
                'premium': user.salarysetup.premium,
                'salary_type': user.salarysetup.salary_type,
                'salary': salary_data.get('calculated_salaries', {}).get(user.id, 0),
                'advance_payment': salary_data.get('salary_advances', {}).get(user.id, 0),
                'penalty': salary_data.get('penalties', {}).get(user.id, 0),
                'month_year': target_month_year
            }
            self.update_or_create(user=user, month_year=target_month_year, defaults=defaults)

    def get_salaries_for_month(self, users, year, month):
        """
        Get all Salary records for a given year and month,
        and return as a dictionary where key is the user_id and value is the Salary object.
        """
        salaries = self.filter(month_year__year=year, month_year__month=month, user__in=users)
        return {salary.user_id: salary for salary in salaries}


class Salary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    completed_amount = models.DecimalField(max_digits=19, decimal_places=0)
    salary = models.DecimalField(max_digits=19, decimal_places=0)
    salary_type = models.CharField(max_length=80, choices=SALARY_TYPE_CHOICES)
    premium = models.FloatField()
    advance_bonus = models.DecimalField(max_digits=19, decimal_places=0, default=0)
    comment = models.TextField(null=True, blank=True)
    penalty = models.DecimalField(max_digits=19, decimal_places=0, default=0)
    pension_contribution = models.DecimalField(max_digits=19, decimal_places=0, default=0)
    advance_payment = models.DecimalField(max_digits=19, decimal_places=0, default=0)
    month_year = models.DateField()
    is_full_payment = models.BooleanField(default=False)
    objects = SalaryManager()

    @property
    def completed_premium(self):
        """
        Вычисляет выполненную суммы, учитывая тип бонуса и значение бонуса.
        """
        effective_amount = Decimal(0)
        if self.salary_type == SALARY_FIXED_PREMIUM:
            effective_amount += self.premium
        elif self.salary_type == SALARY_PERCENTAGE_PREMIUM:
            effective_amount += (self.completed_amount * Decimal(self.premium)) / 100

        return effective_amount

    @property
    def total_amount(self):
        return (
                self.salary +
                self.advance_bonus +
                Decimal(self.completed_premium) -  # преобразование float в Decimal
                self.penalty -
                self.pension_contribution -
                self.advance_payment)


class ProductBonusQueryset(models.QuerySet):

    def bonuses_per_user(self):
        order_content_type = ContentType.objects.get_for_model(Order)

        # Вычисляем сумму, оплаченную для каждого заказа на основе TransactionDetail, учитывая комиссию
        paid_per_order = TransactionDetail.objects.filter(
            transaction__content_type=order_content_type,
            transaction__object_id=OuterRef('product__order__id')
        ).annotate(
            net_paid=ExpressionWrapper(F('price') - (F('price') * F('commission') / 100),
                                       output_field=DecimalField(max_digits=19, decimal_places=2))
        ).values('net_paid').annotate(
            total_paid=Sum('net_paid')
        ).values('total_paid')

        # Определение бонуса на основе типа бонуса и оплаченной суммы
        bonus_calculation = Case(
            When(bonus_type='fixed', then=F('bonus_value')),
            When(bonus_type='percentage', then=ExpressionWrapper(Subquery(paid_per_order) * F('bonus_value') / 100,
                                                                 output_field=DecimalField(max_digits=19,
                                                                                           decimal_places=2))),
            default=Value(0),
            output_field=DecimalField(max_digits=19, decimal_places=2)
        )

        # Группируем по пользователю и суммируем их бонусы
        return self.annotate(
            bonus=bonus_calculation
        ).values('product__order__user__username').annotate(
            total_bonus=Sum('bonus')
        ).order_by('product__order__user__username')


class ProductBonus(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)

    # Поле для выбора типа бонуса
    bonus_type = models.CharField(max_length=10, choices=BONUS_TYPE_CHOICES)

    # Общее поле для значения бонуса
    bonus_value = models.DecimalField(max_digits=8, decimal_places=2)
    objects = ProductBonusQueryset.as_manager()


# class SalaryAdvanceManager(models.Manager):
#
#     def get_total_advance_by_users(self, users, year, month):
#         # Получить все авансы за указанный месяц и год для заданных пользователей
#         advances = self.filter(date__year=year, date__month=month, user__in=users)
#         # Сгруппировать авансы по пользователям и просуммировать их
#         total_advances_by_users = advances.values('user').annotate(
#             total_advance=Sum('advance')).order_by('user')
#
#         # Преобразовать результат в словарь, где ключ - ID пользователя, а значение - общая сумма авансов
#         return {item['user']: item['total_advance'] for item in total_advances_by_users}
#
#
# class SalaryAdvance(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     date = models.DateField()
#     advance = models.DecimalField(max_digits=19, decimal_places=0)
#     comment = models.TextField()
#     objects = SalaryAdvanceManager()

