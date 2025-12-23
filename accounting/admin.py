from django.contrib import admin
from .models import Contractor, Transaction, TransactionDetail, PaymentMethod,\
    TransactionMove, PaymentMethodCommission


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('bank', 'title', 'company')


admin.site.register(Contractor)
admin.site.register(Transaction)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(TransactionDetail)
admin.site.register(TransactionMove)
admin.site.register(PaymentMethodCommission)
