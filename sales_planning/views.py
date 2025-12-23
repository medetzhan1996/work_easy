from django.views.generic import ListView
from django.http import JsonResponse
from django.views.generic.edit import FormView

from content_type_constants import get_content_type_for_model, USER_CT_CACHE_KEY, DEPARTMENT_CT_CACHE_KEY
from account.models import User, Department
from .models import SalesPlan
from .services import create_or_update_sales_plan, annotate_sales_plans
from .utils import get_selected_dates
from .forms import SalesPlanForm


class DepartmentUsersView(ListView):
    template_name = 'sales_planning/department_users.html'
    context_object_name = 'users_by_department'

    def get_queryset(self):
        user = self.request.user

        departments = Department.objects.for_company(user.company).all().prefetch_related(
            'user_set')
        return {department: department.user_set.all() for department in departments}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_periods = []
        selected_period, start_date, end_date = get_selected_dates(
            period=self.request.GET.get('period', None),
            period_val=self.request.GET.get('period_val', None),
            start_date_str=self.request.GET.get('start_date', None),
            end_date_str=self.request.GET.get('end_date', None)
        )
        if selected_period == 'range':
            selected_periods = SalesPlan.objects.group_by_start_end_date()
        user_ct = get_content_type_for_model(User, USER_CT_CACHE_KEY)
        department_ct = get_content_type_for_model(Department, DEPARTMENT_CT_CACHE_KEY)
        annotate_sales_plans(context[self.context_object_name].items(), start_date, end_date)
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'selected_period': selected_period,
            'user_ct': user_ct,
            'department_ct': department_ct,
            'selected_periods': selected_periods
        })
        return context


class SalesPlanFormView(FormView):
    form_class = SalesPlanForm

    def form_valid(self, form):
        data = form.cleaned_data
        sales_plan, created = SalesPlan.objects.update_or_create(
            content_type=data['content_type'],
            object_id=data['object_id'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            defaults={'target_sales': data['target_sales']}
        )
        message = 'Sales Plan successfully created!' if created else 'Sales Plan successfully updated!'
        return JsonResponse({'status': 'success', 'message': message})

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'status': 'error', 'errors': errors}, status=400)

