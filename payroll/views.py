from django.views.generic.base import TemplateResponseMixin, View
from django.http import JsonResponse

from account.models import User
from constants import SALARY_PERCENTAGE_PREMIUM, SALARY_NO_PREMIUM
from content_type_constants import get_content_type_for_model, SALARY_CT_CACHE_KEY
from payroll.models import Salary, Penalty, ProductBonus
from utils import parse_year_month, get_current_year_month, format_year_month
from .forms import get_salary_update_form, PenaltyForm
from .service import SalaryService

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView


class SalaryListView(TemplateResponseMixin, View):
    template_name = 'payroll/salary/list.html'
    model = Salary

    def get(self, request, **kwargs):
        user = request.user
        year_month = request.GET.get('year_month', None)
        year, month = parse_year_month(year_month) if year_month else get_current_year_month()
        selected_year_month = format_year_month(year, month)
        users_in_salary_setup = User.objects.for_company(user.company).filter(salarysetup__isnull=False)

        salary_content_type = get_content_type_for_model(Salary, SALARY_CT_CACHE_KEY)
        salary_users_percentage_data = SalaryService.get_salary_data(users_in_salary_setup, year, month)
        salary_data = salary_users_percentage_data
        Salary.objects.create_or_update_salaries_for_users(users_in_salary_setup, year, month, salary_data)
        salaries = Salary.objects.get_salaries_for_month(users_in_salary_setup, year, month)

        bonuses = ProductBonus.objects.bonuses_per_user()

        return self.render_to_response({
            'users_in_salary_setup': users_in_salary_setup,
            'salaries': salaries,
            'salary_content_type': salary_content_type,
            'year': year,
            'month': month,
            'selected_year_month': selected_year_month,
            'SALARY_PERCENTAGE_PREMIUM': SALARY_PERCENTAGE_PREMIUM,
            'SALARY_NO_PREMIUM': SALARY_NO_PREMIUM
        })


class UpdateSalaryInfo(View):

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        name = request.POST.get('name')
        value = request.POST.get('value')

        try:
            instance = Salary.objects.get(id=user_id)
        except Salary.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Salary not found'})

        # Динамически генерировать класс формы на основе имени поля
        FormClass = get_salary_update_form(name)

        # Инициализировать форму данными POST
        form_data = {name: value}
        form = FormClass(form_data, instance=instance)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            # Возвращать ошибки формы, если проверка не удалась
            return JsonResponse({'status': 'error', 'errors': form.errors})


class PenaltyMixin(LoginRequiredMixin):
    model = Penalty
    context_object_name = 'penalties'

    def get_success_url(self):
        return reverse_lazy('payroll:penalty_list')


class PenaltyEditMixin:
    form_class = PenaltyForm


# Список пакетов программы
class PenaltyListView(PenaltyMixin, ListView):
    template_name = 'payroll/penalty/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        penalties = self.request.GET.get('user', '')
        return qs.filter(user__first_name__icontains=penalties)


# Список пакетов программы
class PenaltyCreateView(PenaltyMixin, PenaltyEditMixin, CreateView):
    template_name = 'payroll/penalty/create.html'

