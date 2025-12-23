from django.views.generic.base import TemplateResponseMixin, View

from account.models import Department
from sales_planning.services import annotate_sales_plans
from sales_planning.utils import get_selected_dates


class UsersRevenue(TemplateResponseMixin, View):
    template_name = 'reports/users_revenue.html'

    def get(self, request):
        selected_period, start_date, end_date = get_selected_dates(
            period='range',
            start_date_str=request.GET.get('start_date', None),
            end_date_str=request.GET.get('end_date', None)
        )
        departments = Department.objects.all()
        return self.render_to_response({
            'departments': departments,
            'start_date': start_date,
            'end_date': end_date
        })
