import json
from django.http import JsonResponse
from django.views.generic import TemplateView, View

from account.models import User
from .mixin_views import WorkTimeMixin, AttendanceMixin
from .forms import AttendanceForm, WorkTimeForm
from .models import WorkTime, Attendance
from utils import month_dates, parse_year_month, get_current_year_month


class BaseContextMixin:

    def get_users(self):
        return User.objects.for_company(self.request.user.company)


class AttendanceView(BaseContextMixin, WorkTimeMixin, AttendanceMixin, TemplateView):
    template_name = 'work_time/attendance/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year_month = self.request.GET.get('month', None)
        if year_month:
            year, month = parse_year_month(year_month)
        else:
            year, month = get_current_year_month()
        users = self.get_users()
        context['users'] = users
        context['dates'] = list(month_dates(year, month))
        context['user_work_times'] = self.get_user_work_times(users)
        context['user_attendances'] = self.get_user_attendances(users, year, month)
        context['current_year'] = year
        context['current_month'] = str(month).zfill(2)
        return context


class WeekWorkTime(BaseContextMixin, WorkTimeMixin, AttendanceMixin, TemplateView):
    template_name = 'work_time/week_work_time/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = 2023
        month = 8
        users = self.get_users()
        context['users'] = users
        context['weekends'] = WorkTime.WEEK_CHOICES
        working_days_for_users = self.get_working_days_for_users(users, year, month)
        context['user_work_times'] = self.get_user_work_times(users)
        calculate_salary_for_date = self.calculate_salary_for_month(
            users, 60000, working_days_for_users, year, month)
        return context


class AttendanceFormView(View):

    def post(self, request, *args, **kwargs):
        form = AttendanceForm(request.POST)
        print(form.is_valid(), 'test..................................status')
        if form.is_valid():
            data = form.cleaned_data

            sales_plan, created = Attendance.objects.update_or_create(
                date=data['date'],
                user=data['user'],
                defaults={'status': data['status']}
            )

            if created:
                message = 'Sales Plan successfully created!'
            else:
                message = 'Sales Plan successfully updated!'

            return JsonResponse({'status': 'success', 'message': message})

        errors = form.errors.as_json()
        return JsonResponse({'status': 'error', 'errors': errors})



class WorkTimeFormView(View):

    def post(self, request, *args, **kwargs):
        form = WorkTimeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            sales_plan, created = WorkTime.objects.update_or_create(
                week=data['week'],
                user=data['user'],
                defaults={'status': data['status']}
            )

            if created:
                message = 'Sales Plan successfully created!'
            else:
                message = 'Sales Plan successfully updated!'

            return JsonResponse({'status': 'success', 'message': message})

        errors = form.errors.as_json()
        return JsonResponse({'status': 'error', 'errors': errors})
