from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'nickname', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'nickname')
    ordering = ('-created_at',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('nickname', 'profile_img', 'preferred_genres'),
        }),
    )
