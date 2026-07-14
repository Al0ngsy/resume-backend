from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

import src.conversation_store as store
from src.conversation_store import create_conversation, get_history
from src.logging_config import getLogger
from src.rate_limiter import limiterIp

router = APIRouter(prefix="/api", tags=["conversations"])
_log = getLogger(__name__)


@router.post("/conversations")
@limiterIp.limit("10/hour")
async def new_conversation(request: Request):
    conv_id = create_conversation()
    _log.info("conversation_created", conversation_id=conv_id)
    return {
        "conversation_id": conv_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    messages = get_history(conversation_id)
    if not messages and conversation_id not in _get_store_ids():
        _log.info("conversation_not_found", conversation_id=conversation_id)
        raise HTTPException(status_code=404, detail="Conversation not found")

    _log.info("conversation_accessed", conversation_id=conversation_id, message_count=len(messages))
    return {
        "conversation_id": conversation_id,
        "message_count": len(messages),
        "messages": [
            {
                "role": m.get("role", "unknown"),
                "content": m.get("content", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            for m in messages
        ],
    }


def _get_store_ids() -> set[str]:
    """Return the set of known conversation IDs (for 404 detection)."""
    return set(store._store.keys())
