import json
from django import forms

from accounting.models import PaymentMethod
from constants import INLINE_FIELD, SELECT, CHECKBOX, DATE, ACCEPTING_PAYMENT, \
    FULL, PAYMENT_METHOD, PAYMENT_CONFIRMATION, BANK, SURCHARGE, DISCOUNT, MATERIAL_BY_CATEGORY
from products.models import Material, Product
from django.contrib.contenttypes.models import ContentType
from .models import FormField
EMPTY_CHOICE = ('', '---------')


class PaymentMethodSelect(forms.Select):
    def __init__(self, attrs=None, choices=(), payment_methods=None):
        self.payment_methods = payment_methods or {}
        super().__init__(attrs, choices)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:
            value_id = json.loads(value).get('id')
            payment_method = self.payment_methods.get(value_id)
            if value_id in self.payment_methods:
                option['attrs']['data-id'] = payment_method.id
                option['attrs']['data-bank'] = payment_method.bank.id
                option['attrs']['data-commission'] = payment_method.commission
            if index != 0:  # this is the default/empty option
                option['attrs']['class'] = 'd-none'  # hide the default/empty option
        return option


class CustomSelect(forms.Select):
    def __init__(self, attrs=None, choices=(), data_list=None):
        super().__init__(attrs, choices)
        self.data_list = data_list

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option_dict = super().create_option(name, value, label, selected, index, subindex=None, attrs=None)
        if value == '':
            option_dict['attrs']['data-id'] = ''
        elif self.data_list:
            data_index = index - 1 if value != '' else index
            if data_index < len(self.data_list):
                data_value = self.data_list[data_index] if subindex is None else self.data_list[data_index][subindex]
                option_dict['attrs']['data-id'] = data_value
        return option_dict


class CreateFieldMixin(forms.Form):

    def create_field(self, field, company):
        field_name = field.name.lower().replace(' ', '_')
        if field.field_type == SELECT:
            self.create_choice_field(field_name, field, field.is_required)
        elif field.field_type == CHECKBOX:
            self.create_boolean_field(field_name, field, field.is_required)
        elif field.field_type == DATE:
            self.create_date_field(field_name, field, field.is_required)
        elif field.field_type == ACCEPTING_PAYMENT:
            self.create_accepting_payment_field(field_name, field, field.is_required)
        elif field.field_type == SURCHARGE:
            self.create_surcharge_field(field_name, field, field.is_required)
        elif field.field_type == DISCOUNT:
            self.create_discount_field(field_name, field, field.is_required)
        elif field.field_type == PAYMENT_METHOD:
            payment_methods = PaymentMethod.objects.filter(company=company, bank__isnull=False).all()
            self.create_payment_method_field(payment_methods, field_name, field, field.is_required)
        elif field.field_type == PAYMENT_CONFIRMATION:
            self.create_payment_confirmation_field(field_name, field, field.is_required)
        elif field.field_type == BANK:
            banks = PaymentMethod.objects.filter(company=company, bank__isnull=True).all()
            self.create_bank_field(banks, field_name, field, field.is_required)
        elif field.field_type == MATERIAL_BY_CATEGORY:
            category = field.associated_object_id
            materials = Material.objects.filter(category__company=company).order_by(
                'title').for_category(category).all()
            self.create_material_by_category_field(materials, field_name, field, field.is_required)



        else:
            self.create_default_field(field_name, field, field.is_required)

    def create_choice_field(self, field_name, field, is_required=False):
        """
        Создайте ChoiceField для формы.
        """
        classes = 'form-control select2'
        widget_attrs = {'class': classes}
        if isinstance(field.choices, list):
            choices_tuple = [EMPTY_CHOICE] + [(choice, choice) for choice in field.choices]
        elif isinstance(field.choices, dict):
            choices_tuple = [EMPTY_CHOICE] + list(field.choices.items())
        else:
            raise ValueError(f"Unexpected type for field.choices in '{field.name}', expected dict or list")
        self.fields[field_name] = forms.ChoiceField(label=field.label, choices=choices_tuple, required=is_required,
                                                    widget=forms.Select(attrs=widget_attrs))

    def create_material_by_category_field(self, materials, field_name, field, is_required=False):
        classes = 'form-control select2'
        widget_attrs = {'class': classes}
        choices_tuple = [EMPTY_CHOICE] + [(json.dumps({'id': material.id, 'label': material.title}), material.title) for
                                          material in materials]
        self.fields[field_name] = forms.ChoiceField(
            label=field.label,
            required=is_required,
            choices=choices_tuple,
            widget=CustomSelect(attrs=widget_attrs, data_list=[material.id for material in materials]))

    def create_bank_field(self, banks, field_name, field, is_required=False):
        """
        Создайте PaymentMethod для формы.
        """
        classes = 'form-control select-bank'
        widget_attrs = {'class': classes}
        choices_tuple = [EMPTY_CHOICE]
        if banks:
            choices_tuple += [(json.dumps({'id': bank.id, 'label': bank.title}), bank.title) for bank in banks]
        self.fields[field_name] = forms.ChoiceField(label=field.label, choices=choices_tuple, required=is_required,
                                                    widget=CustomSelect(
                                                        attrs=widget_attrs, data_list=[bank.id for bank in banks]))

    def create_payment_method_field(self, payment_methods, field_name, field, is_required=False):
        classes = 'form-control payment_method'
        associated_field = field.associated_field
        widget_attrs = {'class': classes}
        if associated_field:
            widget_attrs['data-bank'] = associated_field.name
            widget_attrs['data-id'] = field.id
        choices_tuple = [EMPTY_CHOICE] + [(json.dumps({'id': payment_method.id, 'label': payment_method.title}),
                                           payment_method.title) for payment_method in payment_methods]
        payment_methods_dict = {pm.id: pm for pm in payment_methods}
        self.fields[field_name] = forms.ChoiceField(
            label=field.label,
            choices=choices_tuple,
            required=is_required,
            widget=PaymentMethodSelect(attrs=widget_attrs, payment_methods=payment_methods_dict))

    def create_default_field(self, field_name, field, is_required=False):
        """
        Создайте общее поле для формы.
        """
        classes = 'form-control'
        widget_attrs = {'class': classes}
        field_class = getattr(forms, field.field_type.lower(), forms.CharField)
        self.fields[field_name] = field_class(label=field.label, widget=forms.TextInput(attrs=widget_attrs),
                                              required=is_required)

    def create_boolean_field(self, field_name, field, is_required=False):
        """
        Создайте BooleanField для формы.
        """
        classes = 'form-check-input'
        widget_attrs = {'class': classes}
        field_class = getattr(forms, field.field_type.lower(), forms.BooleanField)
        self.fields[field_name] = field_class(label=field.label, widget=forms.CheckboxInput(attrs=widget_attrs),
                                              required=is_required)

    def create_payment_confirmation_field(self, field_name, field, is_required=False):
        """
        Создайте PAYMENT_CONFIRMATION для формы.
        """
        classes = ''
        widget_attrs = {'class': classes}
        field_class = getattr(forms, field.field_type.lower(), forms.BooleanField)
        self.fields[field_name] = field_class(label=field.label, widget=forms.CheckboxInput(attrs=widget_attrs),
                                              required=is_required)

    def create_hidden_field(self, field_name):
        self.fields[field_name] = forms.CharField(widget=forms.HiddenInput(), required=False)

    def create_date_field(self, field_name, field, is_required=False):
        """
        Создайте DateField для формы.
        """
        classes = 'form-control'
        widget_attrs = {'class': classes, 'type': 'date'}
        field_class = getattr(forms, field.field_type.lower(), forms.DateField)
        self.fields[field_name] = field_class(label=field.label, widget=forms.DateInput(attrs=widget_attrs),
                                              required=is_required)

    def create_decimal_field(self, field_name, field, is_required=False, classes='form-control'):
        """
        Create a DecimalField for the form.
        """
        widget_attrs = {'class': classes}
        associated_field = field.associated_field
        if associated_field:
            widget_attrs['data-associated'] = associated_field.name
        field_class = getattr(forms, field.field_type.lower(), forms.DecimalField)
        self.fields[field_name] = field_class(
            label=field.label,
            widget=forms.NumberInput(attrs=widget_attrs),
            max_digits=19,
            decimal_places=0,
            required=is_required
        )

    def create_integer_field(self, field_name, field, is_required=False, classes='form-control'):
        """
        Create a DecimalField for the form.
        """
        widget_attrs = {'class': classes}
        associated_field = field.associated_field
        if associated_field:
            widget_attrs['data-associated'] = associated_field.name
        field_class = getattr(forms, field.field_type.lower(), forms.IntegerField)
        self.fields[field_name] = field_class(
            label=field.label,
            widget=forms.NumberInput(attrs=widget_attrs),
            required=is_required
        )

    def create_surcharge_field(self, field_name, field, is_required=False):
        """
        Create a DecimalField for the form with 'surcharge' class.
        """
        classes = 'form-control surcharge'
        self.create_integer_field(field_name, field, is_required=is_required, classes=classes)

    def create_discount_field(self, field_name, field, is_required=False):
        """
        Create a DecimalField for the form with 'surcharge' class.
        """
        classes = 'form-control discount'
        self.create_integer_field(field_name, field, is_required=is_required, classes=classes)

    def create_accepting_payment_field(self, field_name, field, is_required=False):
        """
        Create a DecimalField for the accepting_payment with 'accepting_payment' class.
        """
        classes = 'form-control accepting_payment accepting_payment_by_commission'
        self.create_integer_field(field_name, field, is_required=is_required, classes=classes)


class BaseDynamicForm(CreateFieldMixin):
    def __init__(self, company, user_type, model_ct, instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        self.user_type = user_type
        self.model_ct = model_ct
        self.instance = instance

    def _get_form_fields(self, user_type):
        return FormField.objects.select_related('content_type').filter(
            content_type=self.model_ct,
            formfieldpermission__permission=FULL,
            formfieldpermission__user_type=user_type
        ).for_company(self.company).exclude(
            field_type=INLINE_FIELD
        ).all()

    def _is_valid_payment_method(self, value):
        try:
            value_dict = json.loads(value)
            if 'id' in value_dict and 'label' in value_dict:
                return PaymentMethod.objects.filter(company=self.company, id=value_dict['id']).exists()
            else:
                return False
        except json.JSONDecodeError:
            return False

    def _check_required_field(self, required_field, cleaned_data):
        # This is the default implementation.
        # Subclasses can override this method to change the behavior.
        return cleaned_data.get(required_field.name)

    def _get_field_errors(self, cleaned_data, field_name, value):
        errors = []
        form_field = self.form_fields_dict.get(field_name)
        if form_field is None:
            errors.append(forms.ValidationError(f"Field Name: {field_name} does not exist in form_fields"))
        elif value:
            if form_field.field_type == PAYMENT_METHOD and not self._is_valid_payment_method(value):
                errors.append(forms.ValidationError(f"Field Name: {field_name} does not exist in form_fields"))
        return errors

    def clean(self):
        cleaned_data = super().clean()
        errors = []

        for field_name, value in cleaned_data.items():
            errors.extend(self._get_field_errors(cleaned_data, field_name, value))
        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


class DynamicFormDataForm(BaseDynamicForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_fields = self._get_form_fields(self.user_type)
        self.form_fields_dict = {field.name: field for field in self.form_fields}
        for field in self.form_fields:
            self.create_field(field, self.company)


class DynamicSingleDataForm(BaseDynamicForm):
    def __init__(self, field_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.form_field = FormField.objects.filter(
                content_type=self.model_ct, formfieldpermission__permission=FULL,
                formfieldpermission__user_type=self.user_type).get(name=field_name)
            self.create_field(self.form_field, self.company)
            self.form_fields_dict = {self.form_field.name: self.form_field}
        except FormField.DoesNotExist:
            error_message = f"No field matching '{field_name}'"
            self.add_error(None, error_message)

    def _check_required_field(self, required_field, cleaned_data):
        return required_field.name in self.instance.extra_data


class FormFieldForm(forms.ModelForm):
    """
    Form for creating and updating FormField instances
    """
    associated_blocking_field = forms.ModelChoiceField(
        queryset=FormField.objects.none(),
        required=False,
        empty_label='---------',
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        label='Blocking Field'
    )
    
    class Meta:
        model = FormField
        fields = ['label', 'name', 'field_type', 'is_required', 'is_select2', 'choices', 'sorting', 'color', 'styles', 'classes']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Field label'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'field_name'}),
            'field_type': forms.Select(attrs={'class': 'form-control select2'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_select2': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'choices': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '{"key": "value"} or ["value1", "value2"]'}),
            'sorting': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'value': '0'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'styles': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'color: red; font-weight: bold;'}),
            'classes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'custom-class another-class'}),
        }
        labels = {
            'label': 'Label',
            'name': 'Name (field name)',
            'field_type': 'Field Type',
            'is_required': 'Required',
            'is_select2': 'Use Select2',
            'choices': 'Choices (JSON format)',
            'sorting': 'Sort Order',
            'color': 'Color',
            'styles': 'CSS Styles',
            'classes': 'CSS Classes',
        }
        help_texts = {
            'label': 'The display label for this field',
            'name': 'Internal field name (lowercase, underscores only)',
            'field_type': 'The type of input field',
            'is_required': 'Whether this field must be filled',
            'is_select2': 'Enable Select2 for dropdown fields',
            'choices': 'Options for select/radio fields in JSON format',
            'sorting': 'Display order (lower numbers appear first)',
            'color': 'Field color',
            'styles': 'Inline CSS styles',
            'classes': 'CSS class names (space-separated)',
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        self.content_type = kwargs.pop('content_type', None)
        super().__init__(*args, **kwargs)
        
        # Make choices field not required by default
        self.fields['choices'].required = False
        
        # Setup queryset for associated fields
        if self.company and self.content_type:
            associated_fields_qs = FormField.objects.filter(
                company=self.company,
                content_type=self.content_type
            ).exclude(id=self.instance.id if self.instance.pk else None)
            
            self.fields['associated_blocking_field'].queryset = associated_fields_qs
        
        # Add associated_content_type field
        # Get available content types for associated objects
        available_content_types = ContentType.objects.filter(
            model__in=['formfield', 'product', 'material', 'materialcategory', 'paymentmethod']
        ).order_by('model')
        
        self.fields['associated_content_type'] = forms.ModelChoiceField(
            queryset=available_content_types,
            required=False,
            empty_label='---------',
            widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_associated_content_type'}),
            label='Associated Content Type',
            help_text='Type of object this field is associated with'
        )
        
        # Add associated_object_id as a hidden field (will be populated via AJAX)
        self.fields['associated_object_id'] = forms.IntegerField(
            required=False,
            widget=forms.HiddenInput(attrs={'id': 'id_associated_object_id'}),
            label='Associated Object ID'
        )

    def clean_choices(self):
        choices = self.cleaned_data.get('choices')
        field_type = self.cleaned_data.get('field_type')
        
        # Choices are required for select, radio, and datalist
        if field_type in ['select', 'radio', 'datalist']:
            if not choices or (isinstance(choices, str) and not choices.strip()):
                raise forms.ValidationError('Choices are required for select, radio, and datalist field types.')
        
        if choices:
            # If choices is a string, try to parse as JSON
            if isinstance(choices, str):
                try:
                    parsed = json.loads(choices)
                    return parsed
                except json.JSONDecodeError:
                    raise forms.ValidationError('Invalid JSON format. Use {"key": "value"} or ["value1", "value2"]')
            # If it's already a dict or list, return as is
            return choices
        
        return {}

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        if self.content_type:
            instance.content_type = self.content_type
        
        # Handle associated_content_type and associated_object_id
        associated_ct = self.cleaned_data.get('associated_content_type')
        associated_obj_id = self.cleaned_data.get('associated_object_id')
        
        if associated_ct and associated_obj_id:
            # Verify object exists and belongs to company if applicable
            try:
                model_class = associated_ct.model_class()
                if model_class:
                    obj = model_class.objects.get(id=associated_obj_id)
                    
                    # Check if object has company field and it matches
                    if hasattr(obj, 'company') and obj.company != self.company:
                        instance.associated_content_type = None
                        instance.associated_object_id = None
                    else:
                        instance.associated_content_type = associated_ct
                        instance.associated_object_id = associated_obj_id
                else:
                    instance.associated_content_type = None
                    instance.associated_object_id = None
            except Exception:
                # Clear associated field if invalid
                instance.associated_content_type = None
                instance.associated_object_id = None
        else:
            # Clear associated field if not provided
            instance.associated_content_type = None
            instance.associated_object_id = None
        
        # Handle associated_blocking_field is already handled by ModelForm
        
        if commit:
            instance.save()
        return instance

