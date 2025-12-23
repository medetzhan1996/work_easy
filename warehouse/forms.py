from django import forms
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError

from .models import StorageOperation, StorageOperationDetail, StorageOperationMove


class StorageOperationForm(forms.ModelForm):
    class Meta:
        model = StorageOperation
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


class StorageOperationDetailForm(forms.ModelForm):

    class Meta:
        model = StorageOperationDetail
        fields = ['content_type', 'object_id', 'quantity']
        exclude = ('storage_operation', )


class StorageOperationMoveForm(forms.ModelForm):

    class Meta:
        model = StorageOperationMove
        fields = ['storage_from', 'storage_to', 'quantity', 'description']
        exclude = ('company',)

    def clean(self):
        cleaned_data = super().clean()
        storage_from = cleaned_data.get('storage_from')
        storage_to = cleaned_data.get('storage_to')

        if storage_from == storage_to:
            raise ValidationError("Storages must be different.")

        return cleaned_data


def get_storage_operation_detail_formset(instance=None, data=None):
    extra = 0 if instance else 1
    StorageOperationFormSet = inlineformset_factory(
        StorageOperation,
        StorageOperationDetail,
        form=StorageOperationDetailForm,
        extra=extra,
        can_delete=True)
    return StorageOperationFormSet(instance=instance, data=data)
