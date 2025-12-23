from itertools import chain

from django.http import JsonResponse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Product, Material
from .utils import combine_queryset_data


class ProductsSearchView(LoginRequiredMixin, View):
    """ Поиск продукта """

    def get(self, request, *args, **kwargs):
        products = Product.objects.search(
            query=request.GET.get('q')).order_by('title').values('id', 'title')
        return JsonResponse(list(products), safe=False)


class ProductMaterialSearchView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q')
        products = Product.objects.filter(title__icontains=q)[:5]
        materials = Material.objects.filter(
            title__icontains=q)[:5]
        data = list(chain(products, materials))
        result = combine_queryset_data(data)
        return JsonResponse(result, safe=False)