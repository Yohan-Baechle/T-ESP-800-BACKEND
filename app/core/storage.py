import uuid
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def save_document(content: bytes, original_filename: str) -> str:
    """Écrit un document sur disque et retourne son chemin relatif.

    Le nom de fichier stocké est un UUID afin d'éviter les collisions et
    de ne pas exposer le nom d'origine (CDC F1.2).
    """
    storage_dir = Path(settings.storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(original_filename).suffix
    stored_name = f"{uuid.uuid4()}{suffix}"
    destination = storage_dir / stored_name
    destination.write_bytes(content)
    return str(destination)
