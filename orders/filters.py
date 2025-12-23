from datetime import datetime

import django_filters

from account.models import User
from constants import MANAGER
from .models import Order


class MonthFilter(django_filters.CharFilter):
    def filter(self, qs, value):
        if value in django_filters.constants.EMPTY_VALUES:
            return qs
        try:
            year, month = map(int, value.split('-'))
            return qs.filter(create_date__year=year, create_date__month=month)
        except:
            return qs


class OrderFilter(django_filters.FilterSet):
    create_date_month = MonthFilter()

    class Meta:
        model = Order
        fields = ['user', 'create_date_month']

    def __init__(self, *args, **kwargs):
        super(OrderFilter, self).__init__(*args, **kwargs)
        self.form.fields['user'].queryset = User.objects.filter(user_type=MANAGER)

    def get_initial(self):
        initial = super(OrderFilter, self).get_initial()
        current_year_month = datetime.now().strftime('%Y-%m')
        initial['create_date_month'] = current_year_month
        return initial
