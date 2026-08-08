from collections import Counter
from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.constants import MOOD_CHOICES
from apps.common.permissions import IsOwner

from .models import MoodEntry
from .serializers import DailyMoodStatSerializer, MoodEntrySerializer


class MoodEntryViewSet(viewsets.ModelViewSet):
    serializer_class = MoodEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ["mood"]
    search_fields = ["notes"]
    ordering_fields = ["entry_date", "entry_time", "intensity"]

    def get_queryset(self):
        qs = MoodEntry.objects.filter(user=self.request.user)
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(entry_date__gte=start_date)
        if end_date:
            qs = qs.filter(entry_date__lte=end_date)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        latest = self.get_queryset().order_by("-entry_date", "-entry_time").first()
        if not latest:
            return Response(None)
        return Response(MoodEntrySerializer(latest).data)

    @action(detail=False, methods=["get"])
    def weekly(self, request):
        return Response(self._daily_series(days=7))

    @action(detail=False, methods=["get"])
    def monthly(self, request):
        return Response(self._daily_series(days=30))

    @action(detail=False, methods=["get"])
    def choices(self, request):
        return Response([{"value": value, "label": label} for value, label in MOOD_CHOICES])

    def _daily_series(self, days):
        today = timezone.localdate()
        start = today - timedelta(days=days - 1)
        entries = list(self.get_queryset().filter(entry_date__gte=start, entry_date__lte=today))

        by_date = {}
        for entry in entries:
            by_date.setdefault(entry.entry_date, []).append(entry)

        series = []
        for offset in range(days):
            day = start + timedelta(days=offset)
            day_entries = by_date.get(day, [])
            if day_entries:
                avg_intensity = sum(e.intensity for e in day_entries) / len(day_entries)
                dominant_mood = Counter(e.mood for e in day_entries).most_common(1)[0][0]
            else:
                avg_intensity = None
                dominant_mood = None
            series.append(
                {
                    "date": day,
                    "average_intensity": avg_intensity,
                    "dominant_mood": dominant_mood,
                    "entry_count": len(day_entries),
                }
            )

        return DailyMoodStatSerializer(series, many=True).data
