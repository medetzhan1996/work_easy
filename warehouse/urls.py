from django.urls import path
from .views import *
app_name = 'warehouse'

urlpatterns = [
    path('storage_operation/list', StorageOperationListView.as_view(), name='storage_operation_list'),
    path('storage_operation/create', StorageOperationCreateView.as_view(), name='storage_operation_create'),
    path('storage_operation/<int:pk>/update', StorageOperationUpdateView.as_view(), name='storage_operation_update'),
]