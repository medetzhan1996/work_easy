import calendar
from datetime import timedelta
from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models import DateField, IntegerField, Q, F, ExpressionWrapper, DurationField, Count, FloatField
from django.db.models.functions import Extract
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.query import QuerySet

from account.models import User
from sales_planning.utils import is_start_and_end_of_month, is_start_and_end_of_year


class SalesPlanQueryset(QuerySet):

    def get_plan_for_date_range(self, object_id, content_type, start_date, end_date):
        return self.filter(
            content_type=content_type,
            object_id=object_id,
            start_date=start_date,
            end_date=end_date
        ).first()

    def get_plan_for_month(self, object_id, content_type, year, month):
        first_day_of_month = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        last_day_of_month = date(year, month, last_day)
        query = self.get_plan_for_date_range(object_id, content_type, first_day_of_month, last_day_of_month)

        return query.target_sales if query else 0

    def exclude_start_end_month(self):
        return self.filter(
            ~Q(start_date__day=1) | ~Q(end_date__day__in=[30, 31])
        )

    def group_by_start_end_date(self):
        return self.exclude_start_end_month().values('start_date', 'end_date').annotate(count=Count('id'))

    def get_plan_for_year(self, object_id, content_type, year):
        first_day_of_year = date(year, 1, 1)
        last_day_of_year = date(year, 12, 31)
        query = self.get_plan_for_date_range(object_id, content_type, first_day_of_year, last_day_of_year)
        return query.target_sales if query else 0

    def get_proportional_plan(self, object_id, content_type, start, end):
        # Prepare the base query
        selected_days = (end - start).days + 1
        query = self.filter(
            content_type=content_type,
            object_id=object_id,
            start_date__lte=start,
            end_date__gte=end)

        # Annotate the query with the plan's duration and the plan per day
        plans = query.annotate(
            duration=ExpressionWrapper(F('end_date') - F('start_date') + timedelta(days=1),
                                       output_field=DurationField()),
            plan_per_day=ExpressionWrapper(
                F('target_sales') / Extract('duration', 'epoch') * 86400,
                output_field=FloatField())
        ).order_by(
            'duration'
        )
        # Get the most specific plan
        plan = plans.first()
        if plan:
            plan_days = min(plan.duration.days, selected_days)
            # Calculate the proportional plan for the selected period
            proportional_plan = round(plan.plan_per_day * plan_days)
        else:
            proportional_plan = None
        return proportional_plan

    def get_plan(self, object_id, content_type, start, end):
        if is_start_and_end_of_month(start, end) and object_id and content_type:
            # Если даты являются началом и концом месяца и предоставлены object_id и content_type
            return self.get_plan_for_month(object_id, content_type, start.year, start.month)
        elif is_start_and_end_of_year(start, end) and object_id and content_type:
            return self.get_plan_for_year(object_id, content_type, start.year)
        else:
            return self.get_proportional_plan(object_id, content_type, start, end)

    def get_sales_plan_for_employees(self, users, start_date, end_date):
        """
        Получить план продаж для списка работников за указанный период.

        :param users: Список объектов пользователей (работников)
        :param start_date: Дата начала
        :param end_date: Дата конца
        :return: Словарь, где ключ - ID работника, значение - его план продаж за указанный период.
        """
        user_ids = [user.id for user in users]
        content_type = ContentType.objects.get_for_model(User)

        plans = (
            self.filter(
                content_type=content_type,
                object_id__in=user_ids,
                start_date__lte=end_date,
                end_date__gte=start_date
            ).annotate(
                duration_days=ExpressionWrapper(
                    F('end_date') - F('start_date') + timedelta(days=1),
                    output_field=IntegerField()
                ),
                plan_per_day=ExpressionWrapper(
                    F('target_sales') / F('duration_days'),
                    output_field=FloatField()
                )
            ).values_list('object_id', 'plan_per_day')
        )

        selected_days = (end_date - start_date).days + 1

        # Преобразуем результаты в словарь
        plan_dict = {user_id: Decimal('0.00') for user_id in user_ids}
        for user_id, plan_per_day in plans:
            plan_value = Decimal(round(plan_per_day * min(selected_days, plan_per_day)))
            plan_dict[user_id] = plan_value

        return plan_dict


class SalesPlan(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    target_sales = IntegerField()
    start_date = DateField()
    end_date = DateField()
    objects = SalesPlanQueryset.as_manager()
