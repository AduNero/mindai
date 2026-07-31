from django.contrib import admin

from .models import EmergencyResource, Resource, ResourceCategory


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "resource_type", "category", "is_published", "view_count"]
    list_filter = ["resource_type", "is_published"]
    search_fields = ["title", "description"]


@admin.register(EmergencyResource)
class EmergencyResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "country_code", "phone_number", "is_24_7"]
    list_filter = ["country_code"]
