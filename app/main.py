from fastapi import FastAPI

from app.core.config import get_settings
from app.routers import (
    applications,
    auth,
    documents,
    me,
    nursing_offices,
    offers,
    profils,
)

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(profils.router, prefix=settings.api_v1_prefix)
app.include_router(documents.router, prefix=settings.api_v1_prefix)
app.include_router(nursing_offices.router, prefix=settings.api_v1_prefix)
app.include_router(offers.router, prefix=settings.api_v1_prefix)
app.include_router(applications.router, prefix=settings.api_v1_prefix)
app.include_router(me.router, prefix=settings.api_v1_prefix)

# Routers à inclure au fur et à mesure de leur implémentation :
# recherche, communication, admin
