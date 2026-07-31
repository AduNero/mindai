from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import IsOwner

from .models import JournalEntry, Tag
from .serializers import JournalEntrySerializer, JournalReportCreateSerializer, TagSerializer


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    search_fields = ["title", "body"]
    filterset_fields = ["mood", "visibility"]
    ordering_fields = ["entry_date", "created_at"]

    def get_queryset(self):
        qs = JournalEntry.objects.filter(user=self.request.user).prefetch_related("tags")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        tag = self.request.query_params.get("tag")
        if start_date:
            qs = qs.filter(entry_date__gte=start_date)
        if end_date:
            qs = qs.filter(entry_date__lte=end_date)
        if tag:
            qs = qs.filter(tags__name__iexact=tag)
        return qs.distinct()

    def perform_create(self, serializer):
        entry = serializer.save(user=self.request.user)
        self._dispatch_analysis(entry)

    def perform_update(self, serializer):
        entry = serializer.save()
        self._dispatch_analysis(entry)

    @staticmethod
    def _dispatch_analysis(entry):
        from apps.ai_engine.tasks import analyze_content

        analyze_content.delay("journals", "journalentry", str(entry.id))

    @action(detail=False, methods=["get"])
    def stats(self, request):
        qs = self.get_queryset()
        total = qs.count()
        mood_counts = {}
        for entry in qs.only("mood"):
            if entry.mood:
                mood_counts[entry.mood] = mood_counts.get(entry.mood, 0) + 1
        return Response(
            {
                "total_entries": total,
                "public_entries": qs.filter(visibility="public").count(),
                "private_entries": qs.filter(visibility="private").count(),
                "flagged_entries": qs.filter(is_flagged=True).count(),
                "mood_breakdown": mood_counts,
            }
        )


class TagListView(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tag.objects.all().order_by("name")


class JournalReportCreateView(generics.CreateAPIView):
    serializer_class = JournalReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        entry = serializer.save(reported_by=self.request.user)
        entry.journal_entry.is_flagged = True
        entry.journal_entry.save(update_fields=["is_flagged"])
