from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import FormField, FormFieldPermission, DynamicFormData


class FormFieldResource(resources.ModelResource):
    class Meta:
        model = FormField


class FormFieldInline(admin.TabularInline):
    extra = 1
    model = FormFieldPermission


class FormFieldAdmin(ImportExportModelAdmin):
    resource_class = FormFieldResource
    inlines = [FormFieldInline]
    list_filter = (
        "company",
        "field_type",
    )
    search_fields = ("name",)


class FormFieldPermissionResource(resources.ModelResource):
    class Meta:
        model = FormFieldPermission


class FormFieldPermissionAdmin(ImportExportModelAdmin):
    resource_class = FormFieldPermissionResource


admin.site.register(FormField, FormFieldAdmin)

admin.site.register(FormFieldPermission, FormFieldPermissionAdmin)
