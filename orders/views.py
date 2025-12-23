import json

from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin, View
from django.http import JsonResponse
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.shortcuts import redirect
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from account.models import User
from constants import MANAGER, MASTER, ACCOUNTANT_SALES
from content_type_constants import (
    get_content_type_for_model,
    ORDER_CT_CACHE_KEY,
    USER_CT_CACHE_KEY,
    CARD_CT_CACHE_KEY,
)
from accounting.models import PaymentMethod
from dynamic_forms.encoder import DateTimeDecimalEncoder
from dynamic_forms.forms import DynamicFormDataForm, DynamicSingleDataForm
from dynamic_forms.models import FormField
from customers.forms import CustomerForm
from orders.filters import OrderFilter
from products.models import Product
from sales_funnel.models import Card
from sales_planning.models import SalesPlan
from utils import (
    parse_year_month,
    get_current_year_month,
    format_year_month,
    get_last_date,
)
from .models import Order
from .forms import OrderForm, OrderUpdateForm


class BaseMixin:
    order_form_class = OrderForm
    customer_form_class = CustomerForm
    dynamic_form_class = DynamicFormDataForm

    def set_context_data(self, request):
        self.order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
        self.user_ct = get_content_type_for_model(User, USER_CT_CACHE_KEY)
        self.user = request.user

    def form_fields(self, user_type):
        company = self.user.company
        return (
            FormField.objects.filter(
                content_type=self.order_ct,
                company=company,
                formfieldpermission__user_type=user_type,
            )
            .select_related("associated_blocking_field", "content_type", "company")
            .prefetch_related("formfieldpermission_set")
            .order_by("sorting")
            .all()
        )

    def form_sales_fields(self, user_type):
        company = self.user.company
        return (
            FormField.objects.filter(
                content_type=self.order_ct,
                company=company,
                formfieldpermission__user_type=ACCOUNTANT_SALES,
            )
            .select_related("associated_blocking_field", "content_type", "company")
            .prefetch_related("formfieldpermission_set")
            .order_by("sorting")
            .all()
        )

    @cached_property
    def payment_methods(self):
        return PaymentMethod.objects.for_company(self.user.company).prefetch_related(
            "bank"
        )

    def process_form_data(
        self,
        request,
        customer_form_class,
        order_form_class,
        dynamic_form_class,
        user,
        order_ct,
        related_field=None,
    ):
        company = user.company
        user_type = user.user_type
        customer_form = customer_form_class(data=request.POST)
        order_form = order_form_class(data=request.POST, user=user)
        dynamic_form = dynamic_form_class(
            company, user_type, order_ct, data=request.POST
        )
        if all(
            [customer_form.is_valid(), order_form.is_valid(), dynamic_form.is_valid()]
        ):
            instance_customer = customer_form.save(company=company)
            instance_order = order_form.save(commit=False)
            instance_order.customer = instance_customer
            instance_order.extra_data = json.dumps(
                dynamic_form.cleaned_data, cls=DateTimeDecimalEncoder
            )
            instance_order.user = user
            instance_order.item = related_field
            instance_order.save()

            return {
                "id": instance_order.id,
                "status": True,  # Успешно сохранено
            }
        else:
            # Возвращаем статус ошибки
            return {
                "id": None,  # Идентификатор будет None, так как сохранение не удалось
                "status": False,  # Сохранение не удалось
            }

    def process_sales_form_data(
        self,
        request,
        order_form_class,
        dynamic_form_class,
        user,
        order_ct,
        related_field=None,
    ):
        order_form = order_form_class(data=request.POST, user=user)
        company = user.company
        user_type = user.user_type
        dynamic_form = dynamic_form_class(
            company, user_type, order_ct, data=request.POST
        )
        salesman = request.POST.get("salesman", None)
        if all([salesman, order_form.is_valid(), dynamic_form.is_valid()]):
            salesman = get_object_or_404(User, pk=salesman)
            instance_order = order_form.save(commit=False)
            instance_order.salesman = salesman
            instance_order.extra_data = json.dumps(
                dynamic_form.cleaned_data, cls=DateTimeDecimalEncoder
            )
            instance_order.user = user
            instance_order.item = related_field
            instance_order.save()

            return {
                "id": instance_order.id,
                "status": True,  # Успешно сохранено
            }
        else:
            # Возвращаем статус ошибки
            return {
                "id": None,  # Идентификатор будет None, так как сохранение не удалось
                "status": False,  # Сохранение не удалось
            }


class OrderMixin:
    model = Order
    context_object_name = "orders"

    def get_filtered_orders(self, user):
        company = user.company
        orders = Order.objects.order_by("unicode")
        if user.user_type == MANAGER:
            return orders.for_user(user)
        elif user.user_type == MASTER:
            return orders.filter(master=user).for_company(company)
        return orders.for_company(company)

    def get_sales_plan(self, user_id, user_ct, year, month):
        sales_plan = SalesPlan.objects.get_plan_for_month(user_id, user_ct, year, month)
        return sales_plan if sales_plan else 0


class OrderListView(BaseMixin, OrderMixin, TemplateResponseMixin, View):
    template_name = "orders/order/list.html"

    def dispatch(self, request, *args, **kwargs):
        self.set_context_data(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        user = request.user
        company = user.company
        user_type = user.user_type
        date_month = request.GET.get("create_date_month", None)
        year, month = (
            parse_year_month(date_month) if date_month else get_current_year_month()
        )
        plan_for_month = self.get_sales_plan(user.id, self.user_ct, year, month)
        year_month = format_year_month(year, month)
        initial_data = request.GET.copy()
        initial_data["create_date_month"] = year_month
        orders = (
            self.get_filtered_orders(user)
            .filter(customer__isnull=False)
            .order_by("unicode")
        )
        orders_filter = OrderFilter(initial_data, queryset=orders)
        total_sum = orders_filter.qs.total_receipt_amount_for_user(self.user)
        remainder_plan = plan_for_month - total_sum
        customer_form = self.customer_form_class()
        order_form = self.order_form_class(user=self.user)
        dynamic_form = self.dynamic_form_class(company, user_type, self.order_ct)
        last_date = get_last_date(year, month)
        form_fields = self.form_fields(self.user.user_type)
        order_count = orders_filter.qs.count()
        return self.render_to_response(
            {
                "orders_filter": orders_filter,
                "form_fields": form_fields,
                "customer_form": customer_form,
                "order_form": order_form,
                "dynamic_form": dynamic_form,
                "user": self.user,
                "total_sum": total_sum,
                "remainder_plan": remainder_plan,
                "plan_for_month": plan_for_month,
                "last_date": last_date,
                "user_type": user_type,
                "order_count": order_count,
            }
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        process_form_data = self.process_form_data(
            request,
            self.customer_form_class,
            self.order_form_class,
            self.dynamic_form_class,
            self.user,
            self.order_ct,
        )
        return redirect("orders:order_list")


class OrderListSalesView(BaseMixin, OrderMixin, TemplateResponseMixin, View):
    template_name = "orders/order/list.html"

    def dispatch(self, request, *args, **kwargs):
        self.set_context_data(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        user = request.user
        company = user.company
        user_type = ACCOUNTANT_SALES
        date_month = request.GET.get("create_date_month", None)
        year, month = (
            parse_year_month(date_month) if date_month else get_current_year_month()
        )
        plan_for_month = self.get_sales_plan(user.id, self.user_ct, year, month)
        year_month = format_year_month(year, month)
        initial_data = request.GET.copy()
        initial_data["create_date_month"] = year_month
        orders = (
            self.get_filtered_orders(user)
            .filter(salesman__isnull=False)
            .order_by("create_date")
        )
        orders_filter = OrderFilter(initial_data, queryset=orders)
        total_sum = orders_filter.qs.total_receipt_amount_for_user(self.user)
        remainder_plan = plan_for_month - total_sum
        customer_form = self.customer_form_class()
        order_form = self.order_form_class(user=self.user)
        dynamic_form = self.dynamic_form_class(company, user_type, self.order_ct)
        last_date = get_last_date(year, month)
        form_fields = self.form_sales_fields(self.user.user_type)
        return self.render_to_response(
            {
                "orders_filter": orders_filter,
                "form_fields": form_fields,
                "customer_form": customer_form,
                "order_form": order_form,
                "dynamic_form": dynamic_form,
                "user": self.user,
                "total_sum": total_sum,
                "remainder_plan": remainder_plan,
                "plan_for_month": plan_for_month,
                "last_date": last_date,
                "user_type": user_type,
            }
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        process_form_data = self.process_sales_form_data(
            request,
            self.order_form_class,
            self.dynamic_form_class,
            self.user,
            self.order_ct,
        )
        return redirect("orders:order_sales_list")


class OrderCardForm(BaseMixin, OrderMixin, TemplateResponseMixin, View):
    template_name = "orders/order/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.set_context_data(request)
        self.card = get_object_or_404(Card, pk=kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        user = self.user
        company = user.company
        user_type = user.user_type
        customer = self.card.customer
        customer_form = self.customer_form_class(instance=customer)
        order_form = self.order_form_class(user=self.user)
        dynamic_form = self.dynamic_form_class(company, user_type, self.order_ct)
        form_fields = self.form_fields(user_type)
        return self.render_to_response(
            {
                "form_fields": form_fields,
                "customer_form": customer_form,
                "order_form": order_form,
                "dynamic_form": dynamic_form,
                "user": self.user,
                "card_id": self.card.id,
            }
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        result = self.process_form_data(
            request,
            self.customer_form_class,
            self.order_form_class,
            self.dynamic_form_class,
            self.user,
            self.order_ct,
            self.card,
        )
        if result["status"]:
            return JsonResponse({"success": True, "order_id": result["id"]}, status=200)
        return JsonResponse({"success": False}, status=400)


class CardOrderListView(OrderMixin, ListView):
    template_name = "orders/order_card/list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        object_id = self.kwargs.get("object_id")
        content_type = get_content_type_for_model(Card, CARD_CT_CACHE_KEY)
        return queryset.filter(object_id=object_id, content_type=content_type.id).all()


class OrderDeleteView(View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs.get("pk"))
        order.delete()
        return JsonResponse({"status": "success"}, status=200)


class OrderUpdateView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        company = user.company
        user_type = user.user_type
        order_ct = get_content_type_for_model(Order, ORDER_CT_CACHE_KEY)
        order_form = OrderUpdateForm(data=request.POST)
        if order_form.is_valid():
            pk = kwargs.get("pk")
            field_name = order_form.cleaned_data["field_name"]
            new_value = order_form.cleaned_data["new_value"]
            try:
                order = Order.objects.get(id=pk)
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order does not exist"}, status=400)
            if field_name in [field.name for field in Order._meta.get_fields()]:
                if field_name == "product":
                    try:
                        new_value = Product.objects.get(id=new_value)
                    except ObjectDoesNotExist:
                        return JsonResponse(
                            {
                                "error": f"Товар с идентификатором {new_value} не существует"
                            },
                            status=400,
                        )
                elif field_name == "master":
                    try:
                        new_value = User.objects.get(id=new_value)
                    except ObjectDoesNotExist:
                        return JsonResponse(
                            {
                                "error": f"Мастер с идентификатором {new_value} не существует"
                            },
                            status=400,
                        )
                setattr(order, field_name, new_value)
            elif hasattr(order, "extra_data"):
                dynamic_form = DynamicSingleDataForm(
                    field_name=field_name,
                    model_ct=order_ct,
                    company=company,
                    user_type=user_type,
                    instance=order,
                    data={field_name: new_value},
                )
                if dynamic_form.is_valid():
                    extra_data_dict = json.loads(order.extra_data)
                    extra_data_dict[field_name] = new_value
                    order.extra_data = json.dumps(extra_data_dict)
                else:
                    return JsonResponse({"error": dynamic_form.errors}, status=400)
            else:
                return JsonResponse(
                    {"error": f"Invalid field name '{field_name}'"}, status=400
                )

            try:
                order.save()
            except FieldError as e:
                return JsonResponse({"error": str(e)}, status=400)
            except Exception as e:
                return JsonResponse({"error": "Internal server error"}, status=500)

            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"error": order_form.errors}, status=400)
