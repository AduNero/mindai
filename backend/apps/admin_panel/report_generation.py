import csv
import io

from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.appointments.models import Appointment
from apps.assessments.models import AssessmentResult
from apps.journals.models import JournalEntry
from apps.moods.models import MoodEntry


def _collect_summary(user, period_start, period_end):
    moods = MoodEntry.objects.filter(user=user, entry_date__range=(period_start, period_end))
    journals = JournalEntry.objects.filter(user=user, entry_date__range=(period_start, period_end))
    assessments = AssessmentResult.objects.filter(
        user=user, taken_at__date__range=(period_start, period_end)
    ).select_related("assessment_type")
    appointments = Appointment.objects.filter(user=user, scheduled_at__date__range=(period_start, period_end))

    avg_intensity = None
    if moods.exists():
        avg_intensity = sum(m.intensity for m in moods) / moods.count()

    return {
        "mood_entry_count": moods.count(),
        "average_mood_intensity": round(avg_intensity, 2) if avg_intensity is not None else None,
        "journal_entry_count": journals.count(),
        "assessments": list(assessments),
        "appointment_count": appointments.count(),
    }


def build_csv_report(user, period_start, period_end):
    summary = _collect_summary(user, period_start, period_end)
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["MindCare AI — Mental Health Report"])
    writer.writerow(["User", user.email])
    writer.writerow(["Period", f"{period_start} to {period_end}"])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Mood entries logged", summary["mood_entry_count"]])
    writer.writerow(["Average mood intensity", summary["average_mood_intensity"]])
    writer.writerow(["Journal entries written", summary["journal_entry_count"]])
    writer.writerow(["Appointments booked", summary["appointment_count"]])
    writer.writerow([])
    writer.writerow(["Assessment", "Score", "Severity", "Date Taken"])
    for result in summary["assessments"]:
        writer.writerow([result.assessment_type.name, result.total_score, result.severity, result.taken_at.date()])

    return ContentFile(buffer.getvalue().encode("utf-8"), name=f"report-{user.id}-{period_start}-{period_end}.csv")


def build_pdf_report(user, period_start, period_end):
    summary = _collect_summary(user, period_start, period_end)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("MindCare AI — Mental Health Report", styles["Title"]),
        Paragraph(f"User: {user.email}", styles["Normal"]),
        Paragraph(f"Period: {period_start} to {period_end}", styles["Normal"]),
        Spacer(1, 16),
    ]

    summary_table = Table(
        [
            ["Metric", "Value"],
            ["Mood entries logged", summary["mood_entry_count"]],
            ["Average mood intensity", summary["average_mood_intensity"] or "N/A"],
            ["Journal entries written", summary["journal_entry_count"]],
            ["Appointments booked", summary["appointment_count"]],
        ],
        colWidths=[260, 200],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    if summary["assessments"]:
        elements.append(Paragraph("Assessment History", styles["Heading2"]))
        rows = [["Assessment", "Score", "Severity", "Date"]]
        for result in summary["assessments"]:
            rows.append([result.assessment_type.name, result.total_score, result.severity, str(result.taken_at.date())])
        assessment_table = Table(rows, colWidths=[180, 60, 120, 100])
        assessment_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        elements.append(assessment_table)

    elements.append(Spacer(1, 24))
    elements.append(
        Paragraph(
            "This report is generated for personal wellness tracking and is not a clinical or "
            "diagnostic document. If you are in crisis, contact local emergency services.",
            styles["Italic"],
        )
    )

    doc.build(elements)
    return ContentFile(buffer.getvalue(), name=f"report-{user.id}-{period_start}-{period_end}.pdf")
