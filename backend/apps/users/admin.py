from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "pseudonym", "role", "is_active", "is_email_verified", "created_at"]
    list_filter = ["role", "is_active", "is_email_verified"]
    search_fields = ["email", "pseudonym"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Identity", {"fields": ("pseudonym", "role")}),
        (
            "Status",
            {"fields": ("is_active", "is_staff", "is_superuser", "is_email_verified", "groups", "user_permissions")},
        ),
        ("Consent", {"fields": ("age_confirmed_at", "consent_accepted_at")}),
        ("Security", {"fields": ("failed_login_attempts", "locked_until", "last_login_ip")}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "pseudonym", "password1", "password2", "role")}),
    )
    readonly_fields = ["created_at", "last_login"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "theme_preference"]
    search_fields = ["user__email", "user__pseudonym"]
