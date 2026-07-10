from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Per-IP: uses the client's IP address as the key
limiterIp = Limiter(key_func=get_remote_address)

# Per-conversation: uses X-Conversation-ID header, falls back to IP
def _getConversationKey(request: Request) -> str:
    return request.headers.get(
        'X-Conversation-ID', 
        # address as fallback
        get_remote_address(request)
    )

limiterConv = Limiter(key_func=_getConversationKey)

def configureRateLimit(app: FastAPI) -> None:
    # store this on the app state so the routes have access to them
    app.state.limiterIp = limiterIp
    app.state.limiterConv = limiterConv

    @app.exception_handler(RateLimitExceeded)
    async def _rateLimitHandler(exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": str(exc),
            }
        )
    
