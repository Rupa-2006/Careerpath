from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api import admin, assistant, auth, catalog, colleges, journey, profile, reference, skills, path_change
from app.api.deps import Db
from app.core.config import BACKEND_DIR, get_settings

API_PREFIX = "/api/v1"
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
CLIENT_HEADER = "x-careerpath-client"
FRONTEND_BUILD = BACKEND_DIR.parent / "frontend" / "dist"
PAGE_CSP = (
    "default-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; "
    "form-action 'self'; frame-ancestors 'none'"
)

settings = get_settings()
app = FastAPI(
    title="PathMithra API",
    docs_url=None if settings.is_production else "/api/docs",
    redoc_url=None,
    openapi_url=None if settings.is_production else "/api/openapi.json",
)


@app.middleware("http")
async def protect_requests(request: Request, call_next):
    """Blocks forged requests from other sites, and adds browser protections to every response."""
    if request.method in UNSAFE_METHODS and request.url.path.startswith("/api/"):
        origin = request.headers.get("origin")
        allowed = settings.origins | {f"{request.url.scheme}://{request.url.netloc}"}
        if CLIENT_HEADER not in request.headers or (origin and origin not in allowed):
            return JSONResponse({"detail": "This request was blocked."}, status_code=403)

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/docs"):
        return response   # the developer docs page needs outside scripts, and is off in production
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
    else:
        response.headers["Content-Security-Policy"] = PAGE_CSP
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


api = APIRouter(prefix=API_PREFIX)


@api.get("/health", tags=["health"])
def health(db: Db) -> dict[str, str]:
    try:
        db.execute(text("select 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "The database is not available.") from None
    return {"status": "ok"}


api.include_router(auth.router)
api.include_router(profile.router)
api.include_router(reference.router)
api.include_router(catalog.router)
api.include_router(journey.router)
api.include_router(skills.router)
api.include_router(assistant.router)
api.include_router(colleges.router)
api.include_router(colleges.admin_router)
api.include_router(admin.router)
api.include_router(path_change.router)
app.include_router(api)


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    """In production one server does both: built files if they exist, otherwise the React app."""
    if path.startswith("api/") or not FRONTEND_BUILD.exists():
        raise HTTPException(404, "Not found.")
    target = (FRONTEND_BUILD / path).resolve()
    if path and target.is_file() and target.is_relative_to(FRONTEND_BUILD.resolve()):
        return FileResponse(target)
    return FileResponse(Path(FRONTEND_BUILD) / "index.html")
