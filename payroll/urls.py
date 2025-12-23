from django.urls import path
from .views import *
app_name = 'payroll'

urlpatterns = [
    path('salary/list', SalaryListView.as_view(), name='salary_list'),
    path('update_salary/', UpdateSalaryInfo.as_view(), name='update_salary_info'),
    path('penalty/list', PenaltyListView.as_view(), name='penalty_list'),
    path('penalty/create', PenaltyCreateView.as_view(), name='penalty_create'),
]
