from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from account.views import LoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("sales_funnel/", include("sales_funnel.urls", namespace="sales_funnel")),
    path("dynamic_forms/", include("dynamic_forms.urls", namespace="dynamic_forms")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("warehouse/", include("warehouse.urls", namespace="warehouse")),
    path("accounting/", include("accounting.urls", namespace="accounting")),
    path("customers/", include("customers.urls", namespace="customers")),
    path("products/", include("products.urls", namespace="products")),
    path("sales_planning/", include("sales_planning.urls", namespace="sales_planning")),
    path("work_time/", include("work_time.urls", namespace="work_time")),
    path("payroll/", include("payroll.urls", namespace="payroll")),
    path("reports/", include("reports.urls", namespace="reports")),
]
