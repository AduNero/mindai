from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from apps.appointments.models import Appointment, AppointmentStatus
from apps.users.models import CounselorProfile

pytestmark = pytest.mark.django_db


@pytest.fixture
def counselor_profile(counselor_user):
    return CounselorProfile.objects.get(user=counselor_user)


def _future_iso(days=3):
    return (timezone.now() + timedelta(days=days)).isoformat()


class TestBooking:
    def test_book_appointment(self, auth_client, counselor_profile):
        response = auth_client.post(
            "/api/v1/appointments/",
            {"counselor_id": str(counselor_profile.id), "scheduled_at": _future_iso(), "reason_for_visit": "Anxiety"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == AppointmentStatus.PENDING

    def test_cannot_book_in_the_past(self, auth_client, counselor_profile):
        past = (timezone.now() - timedelta(days=1)).isoformat()
        response = auth_client.post(
            "/api/v1/appointments/", {"counselor_id": str(counselor_profile.id), "scheduled_at": past}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_double_book_same_counselor_same_time(self, auth_client, other_auth_client, counselor_profile):
        when = _future_iso()
        first = auth_client.post(
            "/api/v1/appointments/", {"counselor_id": str(counselor_profile.id), "scheduled_at": when}
        )
        assert first.status_code == status.HTTP_201_CREATED

        second = other_auth_client.post(
            "/api/v1/appointments/", {"counselor_id": str(counselor_profile.id), "scheduled_at": when}
        )
        assert second.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_book_counselor_not_accepting(self, auth_client, counselor_profile):
        counselor_profile.is_accepting_appointments = False
        counselor_profile.save()
        response = auth_client.post(
            "/api/v1/appointments/", {"counselor_id": str(counselor_profile.id), "scheduled_at": _future_iso()}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCancelAndReschedule:
    def test_owner_can_cancel_pending_appointment(self, auth_client, user, counselor_profile):
        appointment = Appointment.objects.create(
            user=user, counselor=counselor_profile, scheduled_at=timezone.now() + timedelta(days=2)
        )
        response = auth_client.post(f"/api/v1/appointments/{appointment.id}/cancel/", {"cancellation_reason": "Busy"})
        assert response.status_code == status.HTTP_200_OK
        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.CANCELLED

    def test_cannot_cancel_already_cancelled_appointment(self, auth_client, user, counselor_profile):
        appointment = Appointment.objects.create(
            user=user, counselor=counselor_profile, scheduled_at=timezone.now() + timedelta(days=2),
            status=AppointmentStatus.CANCELLED,
        )
        response = auth_client.post(f"/api/v1/appointments/{appointment.id}/cancel/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_other_user_cannot_cancel_someone_elses_appointment(self, other_auth_client, user, counselor_profile):
        appointment = Appointment.objects.create(
            user=user, counselor=counselor_profile, scheduled_at=timezone.now() + timedelta(days=2)
        )
        response = other_auth_client.post(f"/api/v1/appointments/{appointment.id}/cancel/")
        assert response.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN)

    def test_reschedule_creates_new_appointment_and_marks_old_rescheduled(self, auth_client, user, counselor_profile):
        appointment = Appointment.objects.create(
            user=user, counselor=counselor_profile, scheduled_at=timezone.now() + timedelta(days=2)
        )
        new_time = _future_iso(days=5)

        response = auth_client.post(f"/api/v1/appointments/{appointment.id}/reschedule/", {"scheduled_at": new_time})

        assert response.status_code == status.HTTP_201_CREATED
        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.RESCHEDULED
        assert Appointment.objects.filter(rescheduled_from=appointment).exists()


class TestAdminApproval:
    def test_admin_can_approve_appointment(self, admin_client, user, counselor_profile):
        appointment = Appointment.objects.create(
            user=user, counselor=counselor_profile, scheduled_at=timezone.now() + timedelta(days=2)
        )
        response = admin_client.post(f"/api/v1/appointments/admin/{appointment.id}/approve/")
        assert response.status_code == status.HTTP_200_OK
        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.APPROVED

    def test_regular_user_cannot_approve(self, auth_client, user, counselor_profile):
        appointment = Appointment.objects.create(
            user=user, counselor=counselor_profile, scheduled_at=timezone.now() + timedelta(days=2)
        )
        response = auth_client.post(f"/api/v1/appointments/admin/{appointment.id}/approve/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
