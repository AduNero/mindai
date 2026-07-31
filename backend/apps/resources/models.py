from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import BaseModel


class ResourceCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "resource_categories"
        verbose_name_plural = "Resource Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ResourceType(models.TextChoices):
    ARTICLE = "article", "Article"
    VIDEO = "video", "Video"
    PODCAST = "podcast", "Podcast"
    MEDITATION = "meditation", "Meditation"
    BREATHING_EXERCISE = "breathing_exercise", "Breathing Exercise"
    EMERGENCY = "emergency", "Emergency Resource"


class Resource(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=30, choices=ResourceType.choices)
    category = models.ForeignKey(
        ResourceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="resources"
    )

    body = models.TextField(blank=True, help_text="Full article body (for resource_type=article).")
    external_url = models.URLField(blank=True, help_text="Video/podcast link, for resource_type in (video, podcast).")
    thumbnail = models.ImageField(upload_to="resources/thumbnails/", null=True, blank=True)
    duration_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)

    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="resources_created"
    )

    class Meta:
        db_table = "resources"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["resource_type", "is_published"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title


class EmergencyResource(BaseModel):
    """
    Crisis hotlines / services shown by the Emergency Detection flow,
    filtered by the user's `Profile.country_code`. Falls back to
    `DEFAULT_CRISIS_COUNTRY` (see .env) when the user's country is unknown
    or has no entries.
    """

    country_code = models.CharField(max_length=2, db_index=True, help_text="ISO 3166-1 alpha-2, e.g. 'US', 'GH'.")
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=30, blank=True)
    sms_number = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_24_7 = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default="en")

    class Meta:
        db_table = "emergency_resources"
        indexes = [models.Index(fields=["country_code"])]

    def __str__(self):
        return f"{self.name} ({self.country_code})"
