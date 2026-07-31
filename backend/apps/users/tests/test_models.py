import pytest
from django.utils import timezone

from apps.users.models import Profile

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_full_name_combines_first_and_last(self, user):
        user.first_name, user.last_name = "Ada", "Lovelace"
        assert user.full_name == "Ada Lovelace"

    def test_is_locked_false_when_locked_until_is_none(self, user):
        assert user.is_locked is False

    def test_is_locked_true_when_locked_until_in_future(self, user):
        user.locked_until = timezone.now() + timezone.timedelta(minutes=10)
        assert user.is_locked is True

    def test_is_locked_false_when_locked_until_in_past(self, user):
        user.locked_until = timezone.now() - timezone.timedelta(minutes=10)
        assert user.is_locked is False

    def test_profile_auto_created_on_user_creation(self, user):
        assert Profile.objects.filter(user=user).exists()

    def test_create_superuser_sets_admin_flags(self, db):
        from apps.users.models import Role, User

        admin = User.objects.create_superuser(
            email="root@example.com", password="CorrectHorse42!", first_name="Root", last_name="Admin"
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.role == Role.ADMIN
        assert admin.is_email_verified is True
