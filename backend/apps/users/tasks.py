import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("apps")


@shared_task
def send_verification_email(user_email, first_name, token):
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    send_mail(
        subject=f"Verify your {settings.SITE_NAME} account",
        message=(
            f"Hi {first_name},\n\n"
            f"Welcome to {settings.SITE_NAME}. Please verify your email address "
            f"by visiting the link below (expires in 24 hours):\n\n{link}\n\n"
            f"If you didn't create this account, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


@shared_task
def send_password_reset_email(user_email, first_name, token):
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    send_mail(
        subject=f"Reset your {settings.SITE_NAME} password",
        message=(
            f"Hi {first_name},\n\n"
            f"We received a request to reset your password. This link expires "
            f"in 1 hour:\n\n{link}\n\n"
            f"If you didn't request this, you can safely ignore this email — "
            f"your password will not be changed."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


@shared_task
def send_account_locked_email(user_email, first_name, locked_until_iso):
    send_mail(
        subject=f"{settings.SITE_NAME} — account temporarily locked",
        message=(
            f"Hi {first_name},\n\n"
            f"Your account was temporarily locked after several failed login "
            f"attempts. It will unlock automatically at {locked_until_iso}. "
            f"If this wasn't you, consider resetting your password."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
