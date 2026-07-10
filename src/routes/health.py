import time
from datetime import datetime

from fastapi import APIRouter

from src.logging_config import getLogger

router = APIRouter(prefix="/api", tags=["health"])

_start_time = time.time()
_log = getLogger(__name__)


@router.get("/health")
async def health():
    _log.info("health_check")
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int(time.time() - _start_time),
    }
