import base64

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

pytestmark = pytest.mark.django_db

# A real (if trivial) 1x1 transparent PNG — Django's ImageField loads the
# file through Pillow to verify it's a genuine image, so arbitrary bytes
# with a matching content_type header aren't enough to pass validation.
_ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class TestProfilePictureUpload:
    def test_uploaded_picture_url_is_absolute(self, auth_client):
        """
        Regression test: same class of bug as GeneratedReport's file URL —
        ProfilePictureUploadView serialized the response without
        `context={"request": request}`, so the URL came back as a bare
        "/media/..." path. That only resolves correctly when frontend and
        backend share one origin; on a split deployment (e.g. Vercel +
        Render) the browser resolves it against the frontend's own origin
        instead, and the avatar 404s.
        """
        image = SimpleUploadedFile("avatar.png", _ONE_PIXEL_PNG, content_type="image/png")
        response = auth_client.post("/api/v1/users/me/picture/", {"profile_picture": image}, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile_picture"].startswith("http")
