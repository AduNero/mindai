from rest_framework import serializers

from .models import AdminActionLog


class AdminActionLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source="admin_user.email", read_only=True)

    class Meta:
        model = AdminActionLog
        fields = ["id", "admin_user", "admin_email", "action", "target_model", "target_id", "description", "created_at"]
        read_only_fields = fields
