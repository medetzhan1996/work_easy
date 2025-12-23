from django.db import models
from django.db.models.query import QuerySet

from account.models import Company


class ItemBase(models.Model):
    title = models.CharField(max_length=320)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


# Категория товаров
class MaterialCategory(ItemBase):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class MaterialQueryset(QuerySet):

    def search(self, query):
        return self.filter(title__icontains=query)

    def for_category(self, category):
        return self.filter(category=category)


# Материалы товара
class Material(ItemBase):
    UNIT_CHOICES = (
        (1, "шт"),
        (2, "миллилитр"),
        (3, "грамм"),
        (4, "упаковка"),
        (5, "миллиграмм"),
        (6, "сантиметр"),
        (7, "микролитр"),
        (9, "сетр"),
        (10, "рулон"),
        (11, "литр"),
        (12, "флакон"),
        (13, "единица"),
        (14, "килограмм"),
        (15, "ампула"),
        (16, "коробка"),
        (17, "капсула"),
        (18, "доза"),
        (19, "другое")
    )
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=180, null=True, blank=True)
    sale_unit = models.IntegerField(choices=UNIT_CHOICES, default=0)
    write_off_unit = models.IntegerField(choices=UNIT_CHOICES, default=0)
    unit_equals = models.IntegerField(default=0)
    price = models.DecimalField(
        max_digits=8, decimal_places=1, null=True, blank=True)
    actual_price = models.DecimalField(
        max_digits=8, decimal_places=1, null=True, blank=True)
    critical_amount = models.IntegerField(default=0, null=True, blank=True)
    desired_amount = models.IntegerField(default=0, null=True, blank=True)
    objects = MaterialQueryset.as_manager()


# Категория товаров
class ProductCategory(ItemBase):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='category_product')


class ProductQueryset(QuerySet):

    def search(self, query):
        return self.filter(title__icontains=query)

    def for_company(self, company):
        return self.filter(company=company)


class Product(ItemBase):
    price = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    actual_price = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    objects = ProductQueryset.as_manager()

