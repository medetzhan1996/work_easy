from django.urls import path
from .views import *
app_name = 'sales_funnel'

urlpatterns = [
    path('card/list', CardListView.as_view(), name='card_list'),
    path('card/create', CardCreateView.as_view(), name='card_create'),
    path('card/<int:pk>/update', CardUpdateView.as_view(), name='card_update'),
    path('card-ajax/<int:pk>/update', CardAjaxUpdateView.as_view(), name='card_ajax_update'),
    path('admin_funnel/list', AdminFunnelListView.as_view(), name='admin_funnel_list'),
    path('sort_funnel/update', SortFunnelUpdateView.as_view(), name='sort_funnel_update'),

]