# user/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("numero_tel", "nom", "prenom", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("numero_tel", "nom", "prenom")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("numero_tel", "password")}),
        ("Informations personnelles", {"fields": ("nom", "prenom")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("numero_tel", "nom", "prenom", "password1", "password2"),
        }),
    )