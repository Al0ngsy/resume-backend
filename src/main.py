from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from logging_config import get_bound_logger, get_logger, setup_logging

setup_logging()

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # If the incoming request already has an X-Request-ID header (e.g. from the frontend
        # for an ongoing conversation), reuse it so rateLimitPerConversation can track it.
        # Otherwise, generate a new UUID.
        requestId = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # adds the request ID to the request state so that it can be accessed in the route handlers
        request.state.request_id = requestId
        # forwards the incoming request down the pipeline
        response = await call_next(request)
        # modifies the response before returning it to the client - adding custom header with the request ID
        response.headers["X-Request-ID"] = requestId
        return response
    

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Change this to the frontend URL in production
    allow_methods=["GET", "POST"],
)
app.add_middleware(RequestIDMiddleware)

@app.middleware("http")
async def bind_logger_middleware(request: Request, call_next):
    # Create a bound logger for EVERY incoming request
    request.state.logger = get_bound_logger(
        requestId=request.headers.get("x-request-id", str(uuid.uuid4())),
        conversationId=request.headers.get("x-conversation-id", "unknown"),
        clientId=request.headers.get("x-client-id", "unknown")
    )
    return await call_next(request)

startTime = time.time()

@app.get("/")
async def root():
  return {"hello": "world"}

@app.get("/api/health")
async def health():
  get_logger('health').info("Health check arrives.")
  return {
    "status": "ok",
    "timestamp": datetime.now().isoformat(),       
    "uptimeSeconds": int(time.time() - startTime)
  }

