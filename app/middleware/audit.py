import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import decode_access_token
from app.services.audit import log_event


def _extract_user_id(request: Request) -> uuid.UUID | None:
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("bearer "):
        return None
    subject = decode_access_token(header[7:])
    if subject is None:
        return None
    try:
        return uuid.UUID(subject)
    except ValueError:
        return None


class AuditMiddleware(BaseHTTPMiddleware):
    """Journalise chaque requête API pour la traçabilité (CDC F6.5)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            log_event(
                "http.request",
                user_id=_extract_user_id(request),
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )
        return response
