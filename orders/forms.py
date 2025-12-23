from django import forms

from account.models import User
from constants import MASTER
from products.models import Product
from .models import Order


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        company = self.user.company
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields["product"].queryset = (
            Product.objects.for_company(company).order_by("title").all()
        )
        if self.user:
            self.fields["master"].queryset = User.objects.for_master(company=company)
            self.fields["salesman"].queryset = User.objects.for_salesman(
                company=company
            )

    class Meta:
        model = Order
        fields = ["deadline", "product", "price", "master", "salesman"]
        exclude = (
            "user",
            "customer",
        )


class OrderUpdateForm(forms.Form):
    field_name = forms.CharField(max_length=480)
    new_value = forms.CharField(max_length=480, required=False)


#
# class OrderProductForm(forms.ModelForm):
#     class Meta:
#         model = OrderProduct
#         fields = ['product', 'price', 'count']
#         exclude = ('user', )
#
#
# class DynamicOrderProductForm(OrderProductForm):
#     extra_fields_list = []
#
#     def __init__(self, *args, **kwargs):
#         super(DynamicOrderProductForm, self).__init__(*args, **kwargs)
#         self.add_extra_fields()
#
#     def add_extra_fields(self):
#         for field in self.extra_fields_list:
#             self.fields[field['name']] = forms.CharField(
#                 required=True, label=field['label'],
#                 initial=field.get('initial', ''))


# def get_order_product_formset(instance=None, data=None, extra_fields=[]):
#     extra = 0 if instance.orderproduct_set.count() else 1
#     DynamicOrderProductForm.extra_fields_list = extra_fields
#     OrderFormSet = inlineformset_factory(
#         Order,
#         OrderProduct,
#         form=DynamicOrderProductForm,
#         extra=extra,
#         can_delete=True)
#     return OrderFormSet(instance=instance, data=data)
