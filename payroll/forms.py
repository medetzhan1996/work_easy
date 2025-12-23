from django import forms

from .models import Salary, Penalty


def get_salary_update_form(field_name):
    class DynamicSalaryUpdateForm(forms.ModelForm):
        class Meta:
            model = Salary
            fields = [field_name]
    return DynamicSalaryUpdateForm


class PenaltyForm(forms.ModelForm):

    class Meta:
        model = Penalty
        fields = ['user', 'date', 'penalty', 'comment']