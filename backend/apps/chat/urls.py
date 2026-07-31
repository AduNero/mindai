from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChatSearchView, ChatSessionViewSet

router = DefaultRouter()
router.register("sessions", ChatSessionViewSet, basename="chat-session")

urlpatterns = [
    path("search/", ChatSearchView.as_view(), name="chat-search"),
    *router.urls,
]
