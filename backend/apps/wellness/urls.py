from rest_framework.routers import DefaultRouter

from .views import MeditationSessionViewSet, SleepEntryViewSet

router = DefaultRouter()
router.register("sleep", SleepEntryViewSet, basename="sleep-entry")
router.register("meditation", MeditationSessionViewSet, basename="meditation-session")

urlpatterns = router.urls
