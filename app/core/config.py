from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration applicative chargée depuis l'environnement (.env).

    Aucun secret en clair dans le code (CDC §11.2) : toutes les valeurs
    sensibles proviennent de variables d'environnement.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_name: str = "INFIRMO API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Base de données PostgreSQL
    database_url: str = "postgresql+psycopg://infirmo:infirmo@localhost:5432/infirmo"

    # Redis (WebSocket pub/sub)
    redis_url: str = "redis://localhost:6379/0"

    # Sécurité / JWT (CDC F6.1)
    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Documents légaux (CDC F1.2)
    storage_dir: str = "storage/documents"
    max_document_size_bytes: int = 5 * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance unique des paramètres (mise en cache)."""
    return Settings()
