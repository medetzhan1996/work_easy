from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db.models.query import QuerySet


from constants import USER_TYPE_CHOICES, OWNER, MASTER, SALES


class ItemBase(models.Model):
    title = models.CharField(max_length=180)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


# Список компании
class Company(ItemBase):
    phone_number = models.CharField(max_length=18, null=True, blank=True)
    address = models.CharField(max_length=180, null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "Компании"


class DepartmentQueryset(QuerySet):

    def for_company(self, company):
        return self.filter(company=company)

    def get_departments_with_users(self):
        departments = self.prefetch_related('user_set').all()
        return {department: department.user_set.all() for department in departments}


class Department(ItemBase):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    objects = DepartmentQueryset.as_manager()


class UserQueryset(UserManager):

    def for_company(self, company):
        return self.filter(company=company)

    def for_department(self, department):
        return self.filter(department=department)

    def for_master(self, company):
        query = self.for_company(company)
        return query.filter(user_type=MASTER)

    def for_salesman(self, company):
        query = self.for_company(company)
        return query.filter(user_type=SALES)

    def get_priority(self, is_display=False):
        qs = self
        if is_display:
            qs = qs.filter(is_display=is_display)
        qs = qs.order_by('id').first()
        if qs:
            return qs
        return None


# Расширенный модель пользователя
class User(AbstractUser):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES, default=OWNER)
    telegram_chat_id = models.CharField(max_length=18, null=True, blank=True)
    objects = UserQueryset()
    allowed_add = models.BooleanField(default=True)
    is_display = models.BooleanField(default=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return "{} {}".format(self.last_name, self.first_name)
