from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Generates an RSA private key for OIDC ID token signing and prints it "
        "as a single-line, \\n-escaped PEM string suitable for OIDC_RSA_PRIVATE_KEY "
        "in your .env file. Run once per environment; do not regenerate in place "
        "(it would invalidate any tokens signed with the previous key)."
    )

    def handle(self, *args, **options):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        escaped = pem.replace("\n", "\\n")
        self.stdout.write(self.style.SUCCESS("Add this line to your .env file:"))
        self.stdout.write(f'OIDC_RSA_PRIVATE_KEY="{escaped}"')
