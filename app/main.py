from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.config import APP_NAME, get_settings
from app.core.deps import NotAuthenticated
from app.core.htmx import is_htmx
from app.core.logging import configure_logging, get_logger
from app.core.middleware import IPAllowlistMiddleware, RequestContextMiddleware
from app.core.templating import BASE_DIR, render
from app.routers import accounts, assets, auth, checkin, checkout, locations, people, system, views
from app.services.common import NotFound

log = get_logger("app")

ERROR_TITLES = {
    400: "Bad request",
    401: "Sign in required",
    403: "Access denied",
    404: "Page not found",
    405: "Method not allowed",
    422: "Invalid request",
    500: "Something went wrong",
    503: "Service unavailable",
}


def _error_response(request: Request, status: int, message: str | None = None):
    rid = getattr(request.state, "request_id", "-")
    if is_htmx(request):
        response = Response(message or ERROR_TITLES.get(status, "Error"), status_code=status)
        response.headers["HX-Reswap"] = "none"
        return response
    return render(
        request,
        "errors/error.html",
        {
            "code": status,
            "title": ERROR_TITLES.get(status, "Error"),
            "message": message,
            "request_id": rid,
        },
        status=status,
    )


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    if settings.is_prod and not settings.allowed_networks:
        raise RuntimeError("ALLOWED_IPS must be set when ENV=prod (refusing to start).")

    app = FastAPI(title=APP_NAME, docs_url=None, redoc_url=None, openapi_url=None)

    # Order: last added is outermost. Request context wraps the allowlist, which wraps sessions.
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="assetify_session",
        same_site="lax",
        https_only=settings.session_https_only,
        max_age=None,
    )
    app.add_middleware(IPAllowlistMiddleware)
    app.add_middleware(RequestContextMiddleware)

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        return RedirectResponse("/assets", status_code=303)

    for module in (auth, assets, checkout, checkin, people, locations, system):
        app.include_router(module.router)
    for r in (
        views.operations_router,
        views.warranty_router,
        views.notifications_router,
        views.audit_router,
        accounts.profile_router,
        accounts.users_router,
    ):
        app.include_router(r)

    @app.exception_handler(NotAuthenticated)
    async def not_authenticated(request: Request, exc: NotAuthenticated):
        url = auth.login_redirect_url(request, exc.expired)
        if is_htmx(request):
            response = Response(status_code=204)
            response.headers["HX-Redirect"] = url
            return response
        return RedirectResponse(url, status_code=303)

    @app.exception_handler(NotFound)
    async def not_found(request: Request, exc: NotFound):
        return _error_response(request, 404)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        detail = exc.detail if isinstance(exc.detail, str) and exc.status_code != 404 else None
        return _error_response(request, exc.status_code, detail)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return _error_response(request, 422, "One of the request parameters was not valid.")

    @app.exception_handler(OperationalError)
    async def db_down(request: Request, exc: OperationalError):
        log.exception("database_unavailable")
        return _error_response(request, 503, "The database is temporarily unavailable.")

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        return _error_response(request, 500)

    return app


app = create_app()
