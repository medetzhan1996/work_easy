import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from content_type_constants import get_content_type_for_model, CARD_CT_CACHE_KEY
from customers.forms import CustomerForm
from dynamic_forms.mixin_views import DynamicFormDataMixin
from .models import Card, Funnel
from .forms import CardForm


class CardMixin(object):
    model = Card
    context_object_name = "cards"
    success_url = reverse_lazy("sales_funnel:card_list")

    def dispatch(self, request, *args, **kwargs):
        self.card_ct = get_content_type_for_model(Card, CARD_CT_CACHE_KEY)
        return super().dispatch(request, *args, **kwargs)


class CardEditMixin(CardMixin, DynamicFormDataMixin):
    form_class = CardForm
    customer_form_class = CustomerForm

    def get_object_or_none(self):
        pk = self.kwargs.get("pk", None)
        return self.model.objects.get(pk=pk) if pk else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        instance = self.get_object_or_none()
        customer = instance.customer if instance else None
        context["extra_form"] = self.get_dynamic_form_data(
            company=user.company,
            user_type=user.user_type,
            model_ct=self.card_ct,
            instance=instance,
        )
        context["customer_form"] = self.customer_form_class(instance=customer)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.user.company
        return kwargs

    def post(self, request, *args, **kwargs):
        user = self.request.user
        form = self.form_class(
            data=request.POST, instance=self.get_object_or_none(), company=user.company
        )
        extra_form = self.get_dynamic_form_data(
            company=user.company,
            user_type=user.user_type,
            model_ct=self.card_ct,
            data=request.POST,
            instance=self.get_object_or_none(),
        )
        customer_form = self.customer_form_class(request.POST)
        if all([form.is_valid(), extra_form.is_valid(), customer_form.is_valid()]):
            return self.form_valid(form, extra_form, customer_form)
        else:
            return self.form_invalid(form, extra_form, customer_form)

    def form_valid(self, form, extra_form, customer_form):
        user = self.request.user
        additional_form_data = extra_form.cleaned_data
        form.instance.user = user
        with transaction.atomic():
            customer_obj = customer_form.save(company=user.company)
            obj = form.save(commit=False)
            obj.customer = customer_obj
            obj.save()
            self.save_dynamic_form_data(obj, additional_form_data)
        return JsonResponse({"success": True, "card_id": obj.id})

    def form_invalid(self, form, extra_form, customer_form):
        form_errors = form.errors.as_json()
        customer_form_errors = customer_form.errors.as_json()
        extra_form_errors = extra_form.errors.as_json()
        response_data = {
            "success": False,
            **json.loads(form_errors),
            **json.loads(extra_form_errors),
            **json.loads(customer_form_errors),
        }
        return JsonResponse(response_data)


class CardCreateView(CardEditMixin, CreateView):
    template_name = "sales_funnel/card/form.html"

    def get_initial(self):
        initial = super(CardCreateView, self).get_initial()
        initial["funnel"] = self.request.GET.get("funnel", "")
        return initial


class CardUpdateView(CardEditMixin, UpdateView):
    template_name = "sales_funnel/card/form.html"


class CardListView(CardMixin, ListView):
    template_name = "sales_funnel/card/list.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["funnels"] = (
            Funnel.objects.filter(company=user.company).all().order_by("sorting").all()
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.for_user(self.request.user)


class CardAjaxUpdateView(View):
    model = Card
    form_class = CardForm

    def post(self, request, *args, **kwargs):
        card = get_object_or_404(self.model, pk=kwargs.get("pk"))
        form = self.form_class(
            request.POST,
            instance=card,
            fields=["funnel"],
            company=request.user.company,
        )
        if form.is_valid():
            form.save()
        return JsonResponse({"success": True})


class AdminFunnelMixin(object):
    model = Funnel
    context_object_name = "funnels"
    success_url = reverse_lazy("sales_funnel:admin_funnel_list")

    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(company=user.company).all().order_by("sorting")


class AdminFunnelListView(AdminFunnelMixin, ListView):
    template_name = "sales_funnel/admin_funnel/list.html"


class SortFunnelUpdateView(View):
    def post(self, request):
        sorted_funnels = json.loads(request.POST.get("sorted_funnels", "[]"))
        for index, funnel_id in enumerate(sorted_funnels):
            funnel = Funnel.objects.get(id=int(funnel_id))
            funnel.sorting = index
            funnel.save()
        return JsonResponse({"success": True})
