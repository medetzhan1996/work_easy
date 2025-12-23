from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum


from content_type_constants import get_content_type_for_model, TRANSACTION_CT_CACHE_KEY, \
    OPERATION_METHOD_CONTENT_TYPE_MAP, OPERATION_METHOD_MODEL_MAP
from .filters import StorageOperationFilter
from .forms import StorageOperationForm, get_storage_operation_detail_formset
from .models import StorageOperation, Storage


class StorageOperationMixin(object):
    model = StorageOperation
    success_url = reverse_lazy('warehouse:storage_operation_list')
    filterset_class = StorageOperationFilter

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else self.success_url

    def get_queryset(self):
        company = self.request.user.company
        return super().get_queryset().filter(
            storage_operation_details__isnull=False,
            user__company=company).distinct().order_by('-id')


class StorageOperationEditMixin(StorageOperationMixin):
    form_class = StorageOperationForm
    template_name = 'warehouse/storage_operation/form.html'

    def get_object_or_none(self):
        pk = self.kwargs.get('pk', None)
        return self.model.objects.get(pk=pk) if pk else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['storage_operation_detail_formset'] = get_storage_operation_detail_formset(
            instance=self.get_object_or_none())
        context['related_object'] = self.get_related_object()
        return context

    def get_related_object(self):
        object_id = self.request.GET.get('object_id')
        content_type_id = self.request.GET.get('content_type')
        if object_id and content_type_id:
            try:
                content_type = ContentType.objects.get_for_id(content_type_id)
                return content_type.get_object_for_this_type(pk=object_id)
            except (ObjectDoesNotExist, ValueError):
                return None
        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Получаем данные из GET-параметров или устанавливаем значения по умолчанию
        operation_method = self.request.GET.get('operation_method')
        content_type_cache_key = OPERATION_METHOD_CONTENT_TYPE_MAP.get(operation_method)
        model_for_operation = OPERATION_METHOD_MODEL_MAP.get(operation_method)

        if content_type_cache_key and model_for_operation:
            content_type = get_content_type_for_model(model_for_operation, content_type_cache_key)
            kwargs['content_type'] = content_type
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        operation_method = self.request.GET.get('operation_method')
        if operation_method:
            initial['operation_method'] = operation_method
        return initial

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, instance=self.get_object_or_none())
        storage_operation_detail_formset = get_storage_operation_detail_formset(
            instance=self.get_object_or_none(), data=request.POST)
        print(form.is_valid(), storage_operation_detail_formset.is_valid(),
              storage_operation_detail_formset.errors,
              'error ............................................')
        if all([form.is_valid(), storage_operation_detail_formset.is_valid()]):
            return self.form_valid(form, storage_operation_detail_formset)

    def form_valid(self, form, storage_operation_detail_formset):
        user = self.request.user
        form.instance.user = user
        instance = form.save()
        storage_operation_details = storage_operation_detail_formset.save(
            commit=False
        )
        for storage_operation_detail in storage_operation_details:
            storage_operation_detail.storage_operation = instance
            storage_operation_detail.save()
        return super().form_valid(form)


class StorageOperationListView(StorageOperationMixin, ListView):
    template_name = 'warehouse/storage_operation/list.html'
    context_object_name = 'storage_operations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        storage_operations_filter = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        context['storage_operations_filter'] = storage_operations_filter
        return context


class StorageOperationCreateView(StorageOperationEditMixin, CreateView):
    pass


class StorageOperationUpdateView(StorageOperationEditMixin, UpdateView):
    pass