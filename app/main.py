from fastapi import FastAPI

from app.core.config import get_settings
from app.internal import admin
from app.middleware.audit import AuditMiddleware
from app.routers import (
    applications,
    auth,
    cares,
    communication,
    documents,
    me,
    nursing_offices,
    offers,
    patients,
    profils,
)

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(AuditMiddleware)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(profils.router, prefix=settings.api_v1_prefix)
app.include_router(documents.router, prefix=settings.api_v1_prefix)
app.include_router(nursing_offices.router, prefix=settings.api_v1_prefix)
app.include_router(offers.router, prefix=settings.api_v1_prefix)
app.include_router(applications.router, prefix=settings.api_v1_prefix)
app.include_router(me.router, prefix=settings.api_v1_prefix)
app.include_router(cares.router, prefix=settings.api_v1_prefix)
app.include_router(communication.router, prefix=settings.api_v1_prefix)
app.include_router(patients.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)
