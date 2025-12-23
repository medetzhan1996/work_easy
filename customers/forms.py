from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["full_name", "phone_number", "social_account"]
        exclude = ("company",)

    def save(self, company, commit=True):
        phone_number = self.cleaned_data.get("phone_number")
        social_account = self.cleaned_data.get("social_account")
        full_name = self.cleaned_data.get("full_name")

        customer, created = Customer.objects.update_or_create(
            defaults={"full_name": full_name, "social_account": social_account},
            phone_number=phone_number,
            company=company,
        )
        if commit:
            customer.save()
        return customer
