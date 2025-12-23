from django.urls import path
from . import views
app_name = 'products'

urlpatterns = [
    path('products/search/', views.ProductsSearchView.as_view(), name="products_search"),
    path('products_materials/search/', views.ProductMaterialSearchView.as_view(),
         name="products_materials_search"),

]
