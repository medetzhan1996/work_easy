from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import SalesPlan


class SalesPlanForm(forms.ModelForm):
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        label="Content Type",
        required=True
    )
    object_id = forms.IntegerField(
        label="Object ID",
        required=True,
        widget=forms.NumberInput(attrs={'min': '0'})
    )
    target_sales = forms.IntegerField(
        label="Target Sales",
        required=True,
        widget=forms.NumberInput(attrs={'min': '0'})
    )
    start_date = forms.DateField(
        label="Start Date",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="End Date",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = SalesPlan
        fields = ['content_type', 'object_id', 'target_sales', 'start_date', 'end_date']

    # Если вы хотите добавить дополнительную логику валидации, вы можете переопределить метод `clean`:
    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError({
                    "end_date": "End date cannot be before start date."
                })

        return cleaned_data


class DateRangeForm(forms.Form):
    CHOICES = (
        ('day', 'Day'),
        ('month', 'Month'),
        ('year', 'Year'),
        ('range', 'Range'),
    )

    period = forms.ChoiceField(
        choices=CHOICES,
        required=True,
        initial='month',
        widget=forms.Select
    )

    period_val_month = forms.DateField(
        input_formats=['%Y-%m'],
        required=False,
        widget=forms.DateInput(attrs={'type': 'month'})
    )

    period_val_range_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    period_val_range_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    period_val_year = forms.ChoiceField(
        choices=[('2023', '2023'), ('2024', '2024'), ('2025', '2025')],
        required=False
    )
