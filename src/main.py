import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.rate_limiter import configureRateLimit
from src.logging_config import get_bound_logger, getLogger, setup_logging
from src.routes.chat import router as chat_router
from src.routes.health import router as health_router
from src.routes.conversations import router as conversations_router
from src.routes.admin import router as admin_router

setup_logging()

_log = getLogger(__name__)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Conversation-ID", "X-Request-ID", "X-Client-ID"],
)


# ─── API key authentication ──────────────────────────────────────────
# If API_KEY is set, all /api/* endpoints (except /api/health) require
# the frontend to send `X-API-Key: ***
_HEALTH_PATH = "/api/health"


@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    if settings.api_key and request.url.path.startswith("/api/") and request.url.path != _HEALTH_PATH:
        if request.headers.get("X-API-Key") != settings.api_key:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)


@app.middleware("http")
async def bind_logger_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.logger = get_bound_logger(
        requestId=request_id,
        conversationId=request.headers.get("x-conversation-id", "unknown"),
        clientId=request.headers.get("x-client-id", "unknown"),
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


configureRateLimit(app)

app.include_router(chat_router)
app.include_router(health_router)
app.include_router(conversations_router)

# Admin endpoints (reindex) — available when LOCAL=true or no API_KEY set
if settings.local or not settings.api_key:
    app.include_router(admin_router)


@app.get("/")
async def root():
    _log.info("root_endpoint_called")
    return {"hello": "world"}
