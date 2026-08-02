from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve as serve_static
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
elif getattr(settings, "SERVE_MEDIA_VIA_DJANGO", False):
    # django.conf.urls.static.static() silently no-ops whenever DEBUG is
    # False (checked inside the helper itself, not just our own `if`
    # above), so it can't be reused here even unconditionally — this
    # calls the underlying view directly instead. Only needed for
    # deployments with no reverse proxy in front of Django to serve
    # /media/ directly, the way docker/nginx/nginx.conf does for the
    # VPS path (which never sets SERVE_MEDIA_VIA_DJANGO and never reaches
    # this branch — nginx intercepts /media/ before it gets to Django at
    # all). Free-tier hosting (Render, no reverse proxy) is the deliberate
    # exception — see docs/architecture/free-tier-hosting.md. Django
    # serving media files itself is well-documented as inefficient at
    # real scale; an acceptable tradeoff for that path's traffic level,
    # not for a real production deployment.
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve_static, {"document_root": settings.MEDIA_ROOT}),
    ]
