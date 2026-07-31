import uuid

from django.db import models


class UUIDPrimaryKeyModel(models.Model):
    """
    UUID primary keys instead of sequential integers so that record IDs
    exposed in API responses/URLs (e.g. /journals/<id>/) cannot be
    enumerated to infer platform activity volume — relevant given the
    sensitivity of the data this platform stores.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDPrimaryKeyModel, TimeStampedModel):
    """Standard base for all domain models: UUID pk + created/updated timestamps."""

    class Meta:
        abstract = True
