import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import Text, TypeDecorator

from app.core.config import get_settings

_NONCE_SIZE = 12


def _get_key() -> bytes:
    key = base64.b64decode(get_settings().encryption_key)
    if len(key) != 32:
        raise ValueError("ENCRYPTION_KEY doit être une clé AES-256 (32 octets).")
    return key


def encrypt(plaintext: str) -> str:
    """Chiffre une chaîne en AES-256-GCM (CDC F6.2)."""
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = AESGCM(_get_key()).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt(token: str) -> str:
    """Déchiffre une chaîne produite par ``encrypt``."""
    raw = base64.b64decode(token)
    nonce, ciphertext = raw[:_NONCE_SIZE], raw[_NONCE_SIZE:]
    return AESGCM(_get_key()).decrypt(nonce, ciphertext, None).decode()


class EncryptedString(TypeDecorator):
    """Colonne texte chiffrée au repos en AES-256-GCM (CDC F6.2).

    Le chiffrement est transparent : les valeurs sont chiffrées à l'écriture
    et déchiffrées à la lecture, sans changement pour le code appelant.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        return encrypt(value)

    def process_result_value(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        return decrypt(value)
