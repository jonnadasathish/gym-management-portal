from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import PasswordResetToken, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["email"]
    list_display = ["email", "full_name", "role", "organization", "home_branch", "is_active", "is_staff"]
    list_filter = ["role", "organization", "is_active", "is_staff"]
    search_fields = ["email", "full_name", "phone", "uuid"]
    readonly_fields = ["uuid", "date_joined", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "phone", "uuid")}),
        ("Organization", {"fields": ("organization", "role", "home_branch")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "organization", "role", "home_branch", "password1", "password2"),
            },
        ),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "expires_at", "used_at", "created_at"]
    readonly_fields = ["created_at"]
