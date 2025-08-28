from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the User model.
    """

    list_display = [
        "username",
        "email",
        "get_full_name",
        "role",
        "is_staff",
        "is_active",
        "created_at",
    ]
    list_filter = ["role", "is_staff", "is_active", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name", "github_username"]
    ordering = ["-created_at"]

    fieldsets = list(BaseUserAdmin.fieldsets) + [
        (
            "Profile Information",
            {"fields": ("profile_picture", "bio", "github_username", "role")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    ]

    readonly_fields = ["created_at", "updated_at"]

    add_fieldsets = list(BaseUserAdmin.add_fieldsets) + [
        (
            "Profile Information",
            {"fields": ("email", "first_name", "last_name", "role")},
        ),
    ]

    def get_full_name(self, obj):
        """Display full name in list view."""
        return obj.get_full_name()

    get_full_name.short_description = "Full Name"
