from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image_file(file):
    """Enforce content-type and size limits on user-uploaded images (profile pictures, thumbnails)."""

    content_type = getattr(file, "content_type", None)
    if content_type not in settings.ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(
            f"Unsupported image type '{content_type}'. Allowed: {', '.join(settings.ALLOWED_IMAGE_CONTENT_TYPES)}."
        )
    if file.size > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        raise ValidationError(f"Image exceeds the {max_mb:.0f}MB size limit.")
