from unittest.mock import patch

import factory
import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Role, User


@pytest.fixture(autouse=True)
def _clear_cache():
    """
    DRF's throttle classes (ScopedRateThrottle) count requests via Django's
    cache, which — unlike the database — isn't rolled back between tests.
    Without this, one test's requests against a scope (e.g. "auth") count
    toward every later test's limit in the same run, causing spurious 429s
    far from the throttling test itself.
    """

    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def _mock_sentiment_classifier():
    """
    Journal create/update runs sentiment analysis inline (synchronously,
    no Celery) — see apps.ai_engine.services.analysis. Without this, every
    such test would need a real trained joblib artifact on disk. Patched
    at the consumption point (apps.ai_engine.services.analysis), not
    apps.ai_engine.services.sentiment_classifier, since that's where the
    `from .sentiment_classifier import classify_sentiment` binding lives.
    """

    with patch(
        "apps.ai_engine.services.analysis.classify_sentiment",
        return_value={"label": "neutral", "confidence": 0.5, "model_version": "test-stub"},
    ):
        yield


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    pseudonym = factory.Sequence(lambda n: f"testuser{n}")
    role = Role.USER
    is_active = True
    is_email_verified = True
    age_confirmed_at = factory.LazyFunction(timezone.now)
    consent_accepted_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "CorrectHorse42!")
        if create:
            self.save()


class AdminUserFactory(UserFactory):
    role = Role.ADMIN
    is_staff = True
    is_superuser = True


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def other_user(db):
    """A second, distinct user — for ownership/IDOR isolation tests."""
    return UserFactory()


@pytest.fixture
def admin_user(db):
    return AdminUserFactory()


def _client_for(user):
    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    return _client_for(user)


@pytest.fixture
def other_auth_client(other_user):
    return _client_for(other_user)


@pytest.fixture
def admin_client(admin_user):
    return _client_for(admin_user)
