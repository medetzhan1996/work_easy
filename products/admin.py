from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Product, Material, MaterialCategory, ProductCategory


class ProductResource(resources.ModelResource):

    class Meta:
        model = Product


class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource


class MaterialResource(resources.ModelResource):

    class Meta:
        model = Material


class MaterialAdmin(ImportExportModelAdmin):
    resource_class = MaterialResource


admin.site.register(Product, ProductAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(MaterialCategory)
admin.site.register(ProductCategory)
