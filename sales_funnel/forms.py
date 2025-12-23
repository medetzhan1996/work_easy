from django import forms

from .models import Card, Funnel


class CardForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        editable_fields = kwargs.pop("fields", [])
        instance = kwargs.get("instance", None)
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        # Filter funnel queryset by company
        if company and "funnel" in self.fields:
            self.fields["funnel"].queryset = Funnel.objects.filter(
                company=company
            ).order_by("sorting")

        if instance:
            for field_name in self.fields:
                if field_name not in editable_fields:
                    self[field_name].field.required = False
                    if field_name not in self.data:
                        field_value = getattr(instance, field_name)
                        self.fields[field_name].initial = field_value

    class Meta:
        model = Card
        fields = ["funnel", "notification_date", "comment"]
        exclude = (
            "user",
            "customer",
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        for field_name in self.fields:
            if (
                field_name not in self.cleaned_data
                or self.cleaned_data[field_name] is None
            ):
                setattr(instance, field_name, self.fields[field_name].initial)
        if commit:
            instance.save()
        return instance
