from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


class FormFieldQueryset(QuerySet):
    """A custom queryset for FormField."""

    def for_company(self, company):
        """Get all form fields for a specific company."""
        return self.filter(company=company)

    def get_form_data(self, content_type):
        """Get form data for a specific content type."""
        data = self.filter(content_type=content_type).values_list('name', 'label')
        return [{'name': name, 'label': label, 'initial': ''} for name, label in data]


class DynamicFormQueryset(QuerySet):
    """A custom queryset for DynamicFormData."""

    def get_dynamic_form_data(self, model, object_id=None):
        """Get dynamic form data for a specific model and optional object id."""
        dynamic_form_data = self.filter(
            content_type=ContentType.objects.get_for_model(model)
        )
        if object_id:
            dynamic_form_data = dynamic_form_data.filter(object_id=object_id)
        return {name: value for name, value in dynamic_form_data.values_list('field_name', 'field_value')}