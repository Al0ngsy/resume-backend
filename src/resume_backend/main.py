from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        requestId = str(uuid.uuid4())
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

start_time = time.time()

@app.get("/")
async def root():
  return {"hello": "world"}

@app.get("/api/health")
async def health():
  return {
    "status": "ok",
    "timestamp": datetime.now().isoformat(),       
    "uptime_seconds": int(time.time() - start_time)
  }

