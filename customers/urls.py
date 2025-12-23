from django.urls import path
from . import views
app_name = 'customers'

urlpatterns = [
    path('search/', views.CustomerSearchView.as_view(), name="customer_search"),
    path('customer/create', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customer/<int:pk>/update', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('customer/<int:pk>/detail', views.CustomerDetailView.as_view(), name='customer_detail'),

]
