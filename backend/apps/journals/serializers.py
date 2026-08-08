from rest_framework import serializers

from apps.ai_engine.serializers import SentimentResultSerializer

from .models import JournalEntry, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class TagListField(serializers.ListField):
    child = serializers.CharField(max_length=50)


class JournalEntrySerializer(serializers.ModelSerializer):
    tags = TagListField(source="tag_names", required=False, default=list)
    sentiment = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = [
            "id", "title", "body", "mood", "tags", "entry_date",
            "is_flagged", "sentiment", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_flagged", "sentiment", "created_at", "updated_at"]

    def get_sentiment(self, instance):
        latest = instance.sentiment_results.order_by("-created_at").first()
        return SentimentResultSerializer(latest).data if latest else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["tags"] = list(instance.tags.values_list("name", flat=True))
        return data

    def _sync_tags(self, entry, tag_names):
        tags = [Tag.objects.get_or_create(name=name.strip().lower())[0] for name in tag_names if name.strip()]
        entry.tags.set(tags)

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        entry = JournalEntry.objects.create(**validated_data)
        self._sync_tags(entry, tag_names)
        return entry

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)
        instance = super().update(instance, validated_data)
        if tag_names is not None:
            self._sync_tags(instance, tag_names)
        return instance
