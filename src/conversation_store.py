"""
In-memory conversation store.

Phase 1: Stores conversations in a dict (in-memory).
Phase 2: Replace this module with a database-backed store (e.g. PostgreSQL, Redis).

Each entry is keyed by conversation_id (UUID string) and holds a list of
OpenAI-style ChatCompletionMessageParam dicts with "role" and "content".
"""
import uuid
import threading
from collections.abc import Sequence
from openai.types.chat import ChatCompletionMessageParam

# Global in-memory store: {conversation_id: [messages]}
_store: dict[str, list[ChatCompletionMessageParam]] = {}

# Thread-safe operations (FastAPI is async, but guard against concurrent access)
_lock = threading.Lock()

# Max conversations before oldest are evicted (prevents memory exhaustion)
_MAX_CONVERSATIONS = 500


def create_conversation() -> str:
    """Create a new empty conversation and return its ID."""
    conv_id = str(uuid.uuid4())
    with _lock:
        # Evict oldest conversations if at capacity
        if len(_store) >= _MAX_CONVERSATIONS:
            # Remove ~10% of oldest entries (arbitrary but simple)
            to_remove = len(_store) - _MAX_CONVERSATIONS + 1
            for key in list(_store.keys())[:to_remove]:
                del _store[key]
        _store[conv_id] = []
    return conv_id


def get_history(conversation_id: str) -> list[ChatCompletionMessageParam]:
    """Retrieve the full message history for a conversation.
    Returns an empty list if the conversation doesn't exist yet.
    """
    with _lock:
        return list(_store.get(conversation_id, []))


def append_message(
    conversation_id: str,
    message: ChatCompletionMessageParam,
) -> None:
    """Append a single message to a conversation's history.
    Creates the conversation entry if it doesn't exist.
    """
    with _lock:
        if conversation_id not in _store:
            _store[conversation_id] = []
        _store[conversation_id].append(message)


def append_messages(
    conversation_id: str,
    messages: Sequence[ChatCompletionMessageParam],
) -> None:
    """Append multiple messages to a conversation's history atomically.
    Creates the conversation entry if it doesn't exist.
    """
    with _lock:
        if conversation_id not in _store:
            _store[conversation_id] = []
        _store[conversation_id].extend(messages)


def clear() -> None:
    """Clear all stored conversations (useful for testing)."""
    with _lock:
        _store.clear()