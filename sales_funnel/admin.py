from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Funnel, Card


class FunnelResource(resources.ModelResource):

    class Meta:
        model = Funnel


class FunnelAdmin(ImportExportModelAdmin):
    resource_class = FunnelResource


class CardResource(resources.ModelResource):

    class Meta:
        model = Card


class CardAdmin(ImportExportModelAdmin):
    resource_class = FunnelResource


admin.site.register(Funnel, FunnelAdmin)
admin.site.register(Card, CardAdmin)




