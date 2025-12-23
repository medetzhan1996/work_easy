import django_filters

from .models import StorageOperation


class StorageOperationFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = StorageOperation
        fields = ['operation_method', 'created_at__gte', 'created_at__lte']
