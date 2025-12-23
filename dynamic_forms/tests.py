from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from account.models import Company
from sales_funnel.models import Card
from dynamic_forms.models import DynamicFormData


class DynamicFormDataTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(title='Test Company')
        self.card_content_type = ContentType.objects.get_for_model(Card)

    def test_create_dynamic_form_data(self):
        card = Card.objects.create(name='Test Card')
        additional_form_data = {'field1': 'value1', 'field2': 'value2'}
        DynamicFormData.create_dynamic_form_data(card, additional_form_data)
        dynamic_form_data = DynamicFormData.objects.filter(
            content_type=self.card_content_type,
            object_id=card.id
        )
        self.assertEqual(len(dynamic_form_data), 2)
        self.assertEqual(dynamic_form_data[0].field_name, 'field1')
        self.assertEqual(dynamic_form_data[0].field_value, 'value1')
        self.assertEqual(dynamic_form_data[1].field_name, 'field2')
        self.assertEqual(dynamic_form_data[1].field_value, 'value2')

    def test_create_dynamic_form_data_with_integrity_error(self):
        card = Card.objects.create(name='Test Card')
        DynamicFormData.objects.create(
            field_name='field1',
            field_value='value1',
            content_type=self.card_content_type,
            object_id=card.id
        )
        additional_form_data = {'field1': 'value1', 'field2': 'value2'}
        with self.assertRaises(ValueError):
            DynamicFormData.create_dynamic_form_data(card, additional_form_data)