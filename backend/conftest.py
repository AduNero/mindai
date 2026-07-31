from unittest.mock import MagicMock, patch

import factory
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CounselorProfile, Role, User


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
def _mock_ai_pipelines():
    """
    CELERY_TASK_ALWAYS_EAGER means any incidental analyze_content dispatch
    (e.g. from journal/chat API tests, not just apps.ai_engine's own tests)
    runs synchronously in-process. Without this, that would try to load
    real Hugging Face models on every such test. Dedicated AI tests
    (apps/ai_engine/tests/test_sentiment.py, test_emotion.py) patch these
    same targets again within their own test body for specific outputs,
    which takes precedence over this default for the duration of that test.
    """

    sentiment_pipeline = MagicMock(return_value=[{"label": "NEUTRAL", "score": 0.5}])
    emotion_pipeline = MagicMock(return_value=[[{"label": "neutral", "score": 1.0}]])

    # Patched where each service module *looks up* the name (its own
    # `from .model_loader import get_..._pipeline` binding), not where
    # model_loader defines it — patching the origin wouldn't affect an
    # already-imported reference.
    with (
        patch("apps.ai_engine.services.sentiment.get_sentiment_pipeline", return_value=sentiment_pipeline),
        patch("apps.ai_engine.services.emotion.get_emotion_pipeline", return_value=emotion_pipeline),
    ):
        yield


@pytest.fixture(autouse=True)
def _mock_chat_llm():
    """
    Prevents apps.chat.views.ChatSessionViewSet.send from making a real
    network call to the chat LLM provider during tests. Patched at the
    consumption point (apps.chat.views), not apps.chat.services.llm, for
    the same import-binding reason as _mock_ai_pipelines above. Individual
    tests can override this patch's return value for specific assertions.
    """

    with patch("apps.chat.views.get_chat_reply", return_value="Mocked assistant reply."):
        yield


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = "Test"
    last_name = "User"
    role = Role.USER
    is_active = True
    is_email_verified = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "CorrectHorse42!")
        if create:
            self.save()


class AdminUserFactory(UserFactory):
    role = Role.ADMIN
    is_staff = True
    is_superuser = True


class CounselorUserFactory(UserFactory):
    role = Role.COUNSELOR


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


@pytest.fixture
def counselor_user(db):
    counselor = CounselorUserFactory()
    CounselorProfile.objects.create(
        user=counselor,
        specialization="Anxiety & Stress",
        is_accepting_appointments=True,
        approved_by_admin=True,
    )
    return counselor


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


@pytest.fixture
def counselor_client(counselor_user):
    return _client_for(counselor_user)
