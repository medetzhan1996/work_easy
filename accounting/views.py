from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from content_type_constants import get_content_type_for_model, TRANSACTION_CT_CACHE_KEY, \
    OPERATION_METHOD_CONTENT_TYPE_MAP, OPERATION_METHOD_MODEL_MAP
from .forms import TransactionForm, get_transaction_detail_formset, TransactionMoveForm
from .models import Transaction, PaymentMethod, TransactionMove, TransactionDetail
from .filters import TransactionFilter


class TransactionMixin(object):
    model = Transaction
    success_url = reverse_lazy('accounting:transaction_list')
    filterset_class = TransactionFilter

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else self.success_url

    def get_queryset(self):
        company = self.request.user.company
        return super().get_queryset().filter(
            transaction_details__isnull=False, user__company=company).distinct().order_by('-id')


class TransactionEditMixin(TransactionMixin):
    form_class = TransactionForm
    template_name = 'accounting/transaction/form.html'

    def get_object_or_none(self):
        pk = self.kwargs.get('pk', None)
        return self.model.objects.get(pk=pk) if pk else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction_detail_formset'] = get_transaction_detail_formset(instance=self.get_object_or_none())
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
        transaction_detail_formset = get_transaction_detail_formset(
            instance=self.get_object_or_none(), data=request.POST)
        if all([form.is_valid(), transaction_detail_formset.is_valid()]):
            return self.form_valid(form, transaction_detail_formset)

    def form_valid(self, form, transaction_detail_formset):
        user = self.request.user
        form.instance.user = user
        instance = form.save()
        transaction_details = transaction_detail_formset.save(
            commit=False
        )
        for transaction_detail in transaction_details:
            transaction_detail.transaction = instance
            transaction_detail.save()
        return super().form_valid(form)


class TransactionListView(TransactionMixin, ListView):
    template_name = 'accounting/transaction/list.html'
    context_object_name = 'transactions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        total_sum = Transaction.objects.accounting().aggregate(
            total=Sum('total_sum')
        )['total']
        payment_methods = PaymentMethod.objects.filter(company=user.company, bank__isnull=True).all()
        context['total_sum'] = total_sum
        context['payment_methods'] = payment_methods
        transactions_filter = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        context['transactions_filter'] = transactions_filter
        return context


class TransactionCreateView(TransactionEditMixin, CreateView):
    pass


class TransactionUpdateView(TransactionEditMixin, UpdateView):
    pass


class TransactionMoveMixin(object):
    model = TransactionMove
    success_url = reverse_lazy('accounting:transaction_list')


class TransactionMoveEditMixin(TransactionMoveMixin):
    form_class = TransactionMoveForm
    template_name = 'accounting/transaction_move/form.html'

    def create_or_update_transaction_detail(self, transaction, payment_method, price):
        transaction_detail, created = TransactionDetail.objects.get_or_create(
            transaction=transaction,
            defaults={
                "payment_method": payment_method,
                "price": price
            }
        )

        if not created:
            transaction_detail.price = price
            transaction_detail.payment_method = payment_method
            transaction_detail.save()
        return transaction_detail

    def create_or_update_transaction(self, instance, operation_method, user):
        transaction_move_ct = get_content_type_for_model(Transaction, TRANSACTION_CT_CACHE_KEY)
        transaction, created = Transaction.objects.get_or_create(
            content_type=transaction_move_ct,
            object_id=instance.id,
            operation_method=operation_method,
            defaults={
                "description": instance.description,
                "user": user
            }
        )
        if not created:
            transaction.description = instance.description
            transaction.save()

        return transaction

    def form_valid(self, form):
        user = self.request.user
        form.instance.company = user.company
        instance = form.save()

        transaction_write_off = self.create_or_update_transaction(
            instance,
            Transaction.TRANSFER_WRITE_OFF,
            user
        )
        self.create_or_update_transaction_detail(
            transaction=transaction_write_off,
            payment_method=instance.payment_method_from,
            price=instance.price)

        transaction_replenishment = self.create_or_update_transaction(
            instance,
            Transaction.TRANSFER_REPLENISHMENT,
            user
        )
        self.create_or_update_transaction_detail(
            transaction=transaction_replenishment,
            payment_method=instance.payment_method_to,
            price=instance.price)
        return super().form_valid(form)


class TransactionMoveCreateView(TransactionMoveEditMixin, CreateView):
    pass


class TransactionMoveUpdateView(TransactionMoveEditMixin, UpdateView):
    pass
