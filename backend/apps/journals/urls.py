from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import JournalEntryViewSet, TagListView

router = DefaultRouter()
router.register("", JournalEntryViewSet, basename="journal-entry")

urlpatterns = [
    path("tags/", TagListView.as_view(), name="journal-tags"),
    *router.urls,
]
