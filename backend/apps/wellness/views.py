from django.utils import timezone
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import IsOwner

from .models import MeditationSession, SleepEntry
from .serializers import MeditationSessionSerializer, SleepEntrySerializer


class SleepEntryViewSet(viewsets.ModelViewSet):
    serializer_class = SleepEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    ordering_fields = ["entry_date"]

    def get_queryset(self):
        return SleepEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # SleepEntry has a DB-level unique_together(user, entry_date), but
        # `user` isn't a serializer field (it's set server-side below), so
        # DRF can't auto-generate a UniqueTogetherValidator for it — without
        # this check, a duplicate would surface as an unhandled IntegrityError.
        entry_date = serializer.validated_data["entry_date"]
        if SleepEntry.objects.filter(user=self.request.user, entry_date=entry_date).exists():
            raise serializers.ValidationError(
                {"entry_date": "You already have a sleep entry for this date — edit it instead of creating a new one."}
            )

        entry = serializer.save(user=self.request.user)

        from apps.ai_engine.tasks import recompute_wellness_score

        recompute_wellness_score.delay(str(self.request.user.id), entry.entry_date.isoformat())


class MeditationSessionViewSet(viewsets.ModelViewSet):
    serializer_class = MeditationSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    ordering_fields = ["started_at"]

    def get_queryset(self):
        return MeditationSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        session = serializer.save(user=self.request.user)

        from apps.ai_engine.tasks import recompute_wellness_score

        recompute_wellness_score.delay(str(self.request.user.id), session.started_at.date().isoformat())

    @action(detail=False, methods=["get"])
    def progress(self, request):
        qs = self.get_queryset()
        today = timezone.localdate()
        this_week = qs.filter(started_at__date__gte=today - timezone.timedelta(days=6))
        return Response(
            {
                "total_sessions": qs.count(),
                "total_minutes": sum(qs.values_list("duration_minutes", flat=True)),
                "sessions_this_week": this_week.count(),
                "minutes_this_week": sum(this_week.values_list("duration_minutes", flat=True)),
            }
        )
