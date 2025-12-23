from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['title', 'comment', 'price', 'actual_price']
        exclude = ('user', )
