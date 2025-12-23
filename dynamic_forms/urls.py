from django.urls import path
from .views import (
    AdminFormFieldListView,
    AdminFormFieldCreateView,
    AdminFormFieldDeleteView,
    SortFormFieldUpdateView,
    GetAssociatedObjectsView
)

app_name = "dynamic_forms"

urlpatterns = [
    path(
        "admin_form_field/list",
        AdminFormFieldListView.as_view(),
        name="admin_form_field_list",
    ),
    path(
        "admin_form_field/create",
        AdminFormFieldCreateView.as_view(),
        name="admin_form_field_create",
    ),
    path(
        "admin_form_field/delete",
        AdminFormFieldDeleteView.as_view(),
        name="admin_form_field_delete",
    ),
    path(
        "sort_form_field/update",
        SortFormFieldUpdateView.as_view(),
        name="sort_form_field_update",
    ),
    path(
        "get_associated_objects/",
        GetAssociatedObjectsView.as_view(),
        name="get_associated_objects",
    ),
]
