from django import forms
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError

from .models import Transaction, TransactionDetail, TransactionMove, PaymentMethod


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ('user',)

    def __init__(self, *args, exclude_fields=None, **kwargs):
        operation_method = kwargs.pop('operation_method', None)
        content_type = kwargs.pop('content_type', None)
        super().__init__(*args, **kwargs)

        if exclude_fields is not None:
            for field in exclude_fields:
                self.fields.pop(field, None)

        self.set_hidden_initial_value('operation_method', operation_method)
        self.set_hidden_initial_value('content_type', content_type)

    def set_hidden_initial_value(self, field_name, value):
        if value is not None:
            self.fields[field_name].initial = value
            self.fields[field_name].widget = forms.HiddenInput()


class TransactionDetailForm(forms.ModelForm):
    class Meta:
        model = TransactionDetail
        fields = ['payment_method', 'price']
        exclude = ('transaction', )


class TransactionMoveForm(forms.ModelForm):
    payment_method_from = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(bank__isnull=True),
        required=True
    )
    payment_method_to = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(bank__isnull=True),
        required=True
    )

    class Meta:
        model = TransactionMove
        fields = ['payment_method_from', 'payment_method_to', 'price', 'description']
        exclude = ('company',)

    def clean(self):
        cleaned_data = super().clean()
        payment_method_from = cleaned_data.get('payment_method_from')
        payment_method_to = cleaned_data.get('payment_method_to')

        if payment_method_from == payment_method_to:
            raise ValidationError("Payment methods must be different.")

        return cleaned_data


def get_transaction_detail_formset(instance=None, data=None):
    extra = 0 if instance else 1
    TransactionFormSet = inlineformset_factory(
        Transaction,
        TransactionDetail,
        form=TransactionDetailForm,
        extra=extra,
        can_delete=True)
    return TransactionFormSet(instance=instance, data=data)
