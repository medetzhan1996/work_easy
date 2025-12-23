from django.contrib import admin

from .models import Penalty, SalarySetup, Salary, ProductBonus


admin.site.register(Penalty)
admin.site.register(SalarySetup)
admin.site.register(Salary)
admin.site.register(ProductBonus)


