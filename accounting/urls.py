from django.urls import path
from .views import *
app_name = 'accounting'

urlpatterns = [
    path('transaction/list', TransactionListView.as_view(), name='transaction_list'),
    path('transaction/create', TransactionCreateView.as_view(), name='transaction_create'),
    path('transaction/<int:pk>/update', TransactionUpdateView.as_view(), name='transaction_update'),

    path('transaction_move/create', TransactionMoveCreateView.as_view(), name='transaction_move_create'),
    path('transaction_move/<int:pk>/update', TransactionMoveUpdateView.as_view(), name='transaction_move_update'),
]