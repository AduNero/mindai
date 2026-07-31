from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChatSearchView, ChatSessionViewSet, ChatSyncView, LibreChatSyncNowView

router = DefaultRouter()
router.register("sessions", ChatSessionViewSet, basename="chat-session")

urlpatterns = [
    path("search/", ChatSearchView.as_view(), name="chat-search"),
    path("sync/", ChatSyncView.as_view(), name="chat-sync"),
    path("sync-librechat/", LibreChatSyncNowView.as_view(), name="chat-sync-librechat"),
    *router.urls,
]
