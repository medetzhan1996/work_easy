from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User, Company, Department


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'first_name', 'last_name',
                    'is_staff', 'user_type', 'company', 'department', 'telegram_chat_id')
    list_filter = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'user_type', 'company', 'department')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'company', 'department', 'telegram_chat_id', 'groups')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'allowed_add')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type', 'telegram_chat_id', 'groups'),
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)



admin.site.register(User, CustomUserAdmin)
admin.site.register(Company)
admin.site.register(Department)
