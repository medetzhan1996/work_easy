import json

from django.http import JsonResponse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import Customer
from .forms import CustomerForm


class CustomerMixin(object):
    model = Customer
    context_object_name = 'customers'


class CustomerEditMixin(CustomerMixin):
    form_class = CustomerForm
    template_name = 'customers/customer/form.html'

    def form_invalid(self, form):
        form_errors = form.errors.as_json()
        response_data = {'success': False, **json.loads(form_errors)}
        return JsonResponse(response_data)


class CustomerCreateView(CustomerEditMixin, CreateView):

    def form_valid(self, form):
        instance = form.save(self.request.user.company)
        return JsonResponse({
            'success': True, 'id': instance.id,
            'full_name': instance.full_name})


class CustomerUpdateView(CustomerEditMixin, UpdateView):

    def form_valid(self, form):
        instance = form.save(self.request.user.company)
        return JsonResponse({
            'success': True, 'id': instance.id,
            'full_name': form.instance.full_name})


class CustomerDetailView(CustomerMixin, DetailView):
    template_name = 'customers/customer/detail.html'
    context_object_name = 'customer'


class CustomerSearchView(LoginRequiredMixin, View):
    """ Поиск клиента """

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.search(
            query=request.GET.get('q')).values('id', 'full_name')
        return JsonResponse(list(customers), safe=False)


