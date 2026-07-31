from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def health_check(request):
    return JsonResponse({"status": "ok", "service": "MindCare AI API"})


api_v1_patterns = [
    path("auth/", include("apps.users.urls.auth")),
    path("users/", include("apps.users.urls.users")),
    path("moods/", include("apps.moods.urls")),
    path("journals/", include("apps.journals.urls")),
    path("wellness/", include("apps.wellness.urls")),
    path("assessments/", include("apps.assessments.urls")),
    path("ai/", include("apps.ai_engine.urls")),
    path("recommendations/", include("apps.recommendations.urls")),
    path("chat/", include("apps.chat.urls")),
    path("appointments/", include("apps.appointments.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("resources/", include("apps.resources.urls")),
    path("admin-panel/", include("apps.admin_panel.urls")),
    path("audit/", include("apps.audit.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("api/v1/", include(api_v1_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
