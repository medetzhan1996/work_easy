from django.urls import path
from .views import *
app_name = 'sales_planning'

urlpatterns = [
    path('department/users', DepartmentUsersView.as_view(), name='department_users'),
    path('sales_plan/form/', SalesPlanFormView.as_view(), name='sales_plan_form'),

]