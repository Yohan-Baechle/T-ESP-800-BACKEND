import pyotp

from app.core.config import get_settings

settings = get_settings()


def generate_secret() -> str:
    """Génère un secret TOTP base32 (CDC F1.4)."""
    return pyotp.random_base32()


def provisioning_uri(secret: str, account: str) -> str:
    """Retourne l'URI otpauth:// à encoder en QR code pour l'application 2FA."""
    return pyotp.TOTP(secret).provisioning_uri(
        name=account, issuer_name=settings.app_name
    )


def verify_code(secret: str, code: str) -> bool:
    """Vérifie un code TOTP fourni par l'utilisateur (tolérance ±1 intervalle)."""
    return pyotp.TOTP(secret).verify(code, valid_window=1)
