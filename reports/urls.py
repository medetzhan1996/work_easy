from django.urls import path
from .views import *
app_name = 'reports'

urlpatterns = [
    path('sales/', UsersRevenue.as_view(), name='users_revenue'),

]
