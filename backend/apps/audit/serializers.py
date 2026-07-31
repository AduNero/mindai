from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id", "user", "user_email", "action", "model_name", "object_id",
            "ip_address", "user_agent", "metadata", "created_at",
        ]
        read_only_fields = fields
