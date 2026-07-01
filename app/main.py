from fastapi import FastAPI

from app.core.config import get_settings
from app.routers import auth, profils

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(profils.router, prefix=settings.api_v1_prefix)

# Routers à inclure au fur et à mesure de leur implémentation :
# documents, recherche, remplacements, communication, admin
