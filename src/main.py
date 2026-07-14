from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
import socket
import uuid

from src.config import settings
from src.rate_limiter import configureRateLimit
from src.logging_config import get_bound_logger, getLogger, setup_logging
from src.routes.chat import router as chat_router
from src.routes.health import router as health_router
from src.routes.conversations import router as conversations_router

setup_logging()

_log = getLogger(__name__)


def _collect_routes(routes, prefix: str = "") -> list[tuple[str, str]]:
    """Recursively collect (methods, path) from FastAPI routes, including included routers."""
    result: list[tuple[str, str]] = []
    for route in routes:
        if isinstance(route, APIRoute) and route.methods:
            methods = ",".join(sorted(route.methods - {"HEAD", "OPTIONS"}))
            result.append((methods, prefix + route.path))
        elif hasattr(route, "original_router"):
            result.extend(_collect_routes(route.original_router.routes, prefix)) # type: ignore
    return result


def print_routes(app: FastAPI) -> None:
    """Print the hostname and all registered REST API routes at server start."""
    hostname = socket.gethostname()
    _log.info("server_starting", hostname=hostname)
    print(f"\n{'='*60}")
    print(f"  Server starting on host: {hostname}")
    print(f"{'='*60}")
    print(f"  Registered API endpoints:")
    print(f"  {'─'*56}")
    for methods, path in sorted(_collect_routes(app.routes)):
        print(f"    {methods:7s}  {path}")
    print(f"{'='*60}\n")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        requestId = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = requestId
        response = await call_next(request)
        response.headers["X-Request-ID"] = requestId
        return response


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Conversation-ID", "X-Request-ID", "X-Client-ID"],
)
app.add_middleware(RequestIDMiddleware)


# ─── API key authentication ──────────────────────────────────────────
# If API_KEY is set, all /api/* endpoints (except /api/health) require
# the frontend to send `X-API-Key: <key>`.
_HEALTH_PATH = "/api/health"


@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    if settings.api_key and request.url.path.startswith("/api/") and request.url.path != _HEALTH_PATH:
        if request.headers.get("X-API-Key") != settings.api_key:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)


@app.middleware("http")
async def bind_logger_middleware(request: Request, call_next):
    request.state.logger = get_bound_logger(
        requestId=request.headers.get("x-request-id", str(uuid.uuid4())),
        conversationId=request.headers.get("x-conversation-id", "unknown"),
        clientId=request.headers.get("x-client-id", "unknown"),
    )
    return await call_next(request)


configureRateLimit(app)

app.include_router(chat_router)
app.include_router(health_router)
app.include_router(conversations_router)


@app.get("/")
async def root():
    _log.info("root_endpoint_called")
    return {"hello": "world"}


print_routes(app)
