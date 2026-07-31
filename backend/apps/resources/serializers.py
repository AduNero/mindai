from rest_framework import serializers

from apps.common.validators import validate_image_file

from .models import EmergencyResource, Resource, ResourceCategory


class ResourceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceCategory
        fields = ["id", "name", "slug", "description"]
        read_only_fields = ["id", "slug"]


class ResourceSerializer(serializers.ModelSerializer):
    category = ResourceCategorySerializer(read_only=True)

    class Meta:
        model = Resource
        fields = [
            "id", "title", "description", "resource_type", "category", "body",
            "external_url", "thumbnail", "duration_minutes", "tags",
            "is_published", "view_count", "created_at",
        ]
        read_only_fields = ["id", "view_count", "created_at"]


class ResourceWriteSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(required=False, validators=[validate_image_file])
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=ResourceCategory.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Resource
        fields = [
            "title", "description", "resource_type", "category_id", "body",
            "external_url", "thumbnail", "duration_minutes", "tags", "is_published",
        ]


class EmergencyResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyResource
        fields = [
            "id", "country_code", "name", "phone_number", "sms_number",
            "website", "description", "is_24_7", "language",
        ]
        read_only_fields = ["id"]
