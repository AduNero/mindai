import os
from unittest.mock import patch

import pytest
from django.core.management import call_command

from apps.users.models import User

pytestmark = pytest.mark.django_db


class TestBootstrapAdmin:
    def test_noop_when_env_vars_unset(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DJANGO_SUPERUSER_EMAIL", None)
            os.environ.pop("DJANGO_SUPERUSER_PASSWORD", None)
            call_command("bootstrap_admin")

        assert User.objects.count() == 0

    def test_creates_superuser_from_env_vars(self):
        env = {"DJANGO_SUPERUSER_EMAIL": "admin@example.com", "DJANGO_SUPERUSER_PASSWORD": "SuperSecret42!"}
        with patch.dict(os.environ, env):
            call_command("bootstrap_admin")

        user = User.objects.get(email="admin@example.com")
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.check_password("SuperSecret42!")

    def test_rerunning_updates_existing_user_instead_of_erroring(self):
        env = {"DJANGO_SUPERUSER_EMAIL": "admin@example.com", "DJANGO_SUPERUSER_PASSWORD": "FirstPassword1!"}
        with patch.dict(os.environ, env):
            call_command("bootstrap_admin")

        env["DJANGO_SUPERUSER_PASSWORD"] = "SecondPassword2!"
        with patch.dict(os.environ, env):
            call_command("bootstrap_admin")

        assert User.objects.filter(email="admin@example.com").count() == 1
        user = User.objects.get(email="admin@example.com")
        assert user.check_password("SecondPassword2!")
