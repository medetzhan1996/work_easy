from django.contrib import admin

from .models import Order, OrderDetail


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "unicode",
        "customer",
        "product",
        "price",
        "user",
        "master",
        "salesman",
        "deadline",
        "create_date",
    ]
    list_filter = [
        "create_date",
        "deadline",
        "user__company",
        "user",
    ]
    search_fields = [
        "unicode",
        "customer__full_name",
        "customer__phone_number",
        "product__title",
    ]
    readonly_fields = ["unicode", "day_index", "create_date", "total_receipt_amount"]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("unicode", "customer", "product", "price", "deadline")},
        ),
        ("Сотрудники", {"fields": ("user", "master", "salesman")}),
        (
            "Дополнительно",
            {
                "fields": (
                    "extra_data",
                    "total_receipt_amount",
                    "day_index",
                    "create_date",
                )
            },
        ),
    )


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ["id", "order"]
    list_filter = ["order"]
