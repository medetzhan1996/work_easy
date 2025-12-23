from dynamic_forms.forms import DynamicFormDataForm
from dynamic_forms.models import DynamicFormData


class DynamicFormDataMixin(object):
    dynamic_form_data_class = DynamicFormDataForm

    def get_dynamic_form_data(self, company, user_type, model_ct, instance=None, data=None):
        initial_data = {}
        if instance:
            initial_data = self.get_dynamic_form_fields(self.model, instance.id)
        return self.dynamic_form_data_class(company, user_type, model_ct=model_ct,
                                            initial=initial_data, data=data)

    def get_dynamic_form_fields(self, model, object_id):
        return DynamicFormData.objects.get_dynamic_form_data(model, object_id)

    def save_dynamic_form_data(self, obj, additional_form_data, instance=None):
        if instance:
            pass
        else:
            DynamicFormData.create_dynamic_form_data(obj, additional_form_data)