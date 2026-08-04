from django.db import migrations


def fix_column_drift(apps, schema_editor):
    """
    Render's live Postgres still carries the schema left behind by
    0002_emailverificationtoken_attempts_and_more — a migration that
    narrowed `token` to varchar(6) and added an `attempts` column for the
    since-reverted OTP feature. Deleting that migration file when OTP was
    rolled back only removed Django's record of how to reverse it; it
    didn't touch the already-applied database schema, so Postgres kept
    rejecting new (long, link-style) tokens with "value too long for
    type character varying(6)". This repairs it directly.

    Local/test databases (sqlite) never had that migration applied —
    they were always at the varchar(255) baseline from 0001 — so there's
    nothing to fix there.
    """
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("ALTER TABLE email_verification_tokens ALTER COLUMN token TYPE varchar(255)")
        cursor.execute("ALTER TABLE password_reset_tokens ALTER COLUMN token TYPE varchar(255)")
        cursor.execute("ALTER TABLE email_verification_tokens DROP COLUMN IF EXISTS attempts")
        cursor.execute("ALTER TABLE password_reset_tokens DROP COLUMN IF EXISTS attempts")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(fix_column_drift, migrations.RunPython.noop),
    ]
