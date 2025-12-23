from django.urls import path
from .views import *

app_name = "orders"

urlpatterns = [
    path("order/list/", OrderListView.as_view(), name="order_list"),
    path("order_sales/list/", OrderListSalesView.as_view(), name="order_sales_list"),
    path("order/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("order/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("order/card/<int:pk>/form/", OrderCardForm.as_view(), name="order_card_form"),
    path(
        "card_order/<int:object_id>/list/",
        CardOrderListView.as_view(),
        name="card_order_list",
    ),
]
