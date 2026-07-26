"""
Database-backed conversation store.

Replaces the former in-memory dict store with SQLAlchemy async calls against
the PostgreSQL database. Function names are preserved so route code only
needs to add `await`.

Each conversation row owns many message rows. get_history returns a list of
{"role": ..., "content": ...} dicts (OpenAI ChatCompletionMessageParam format).
"""
import uuid
from collections.abc import Sequence

from sqlalchemy import delete, select

from openai.types.chat import ChatCompletionMessageParam

from src.db.database import _ensure_engine
from src.db.models import Conversation, Message


async def create_conversation() -> str:
    """Create a new empty conversation and return its ID (UUID string)."""
    _ensure_engine()
    from src.db.database import AsyncSessionLocal
    conv = Conversation(id=uuid.uuid4())
    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        session.add(conv)
        await session.commit()
        return str(conv.id)


async def conversation_exists(conversation_id: str) -> bool:
    """Return True if a conversation with the given ID exists in the DB."""
    _ensure_engine()
    from src.db.database import AsyncSessionLocal
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except (ValueError, AttributeError):
        return False
    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        result = await session.execute(
            select(Conversation.id).where(Conversation.id == conv_uuid)
        )
        return result.scalar_one_or_none() is not None


async def get_history(conversation_id: str) -> list[ChatCompletionMessageParam]:
    """Retrieve the full message history for a conversation.

    Returns an empty list if the conversation doesn't exist yet.
    """
    _ensure_engine()
    from src.db.database import AsyncSessionLocal
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except (ValueError, AttributeError):
        return []
    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(Message.created_at, Message.id)
        )
        messages = result.scalars().all()
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]  # type: ignore[return-value]


async def append_message(
    conversation_id: str,
    message: ChatCompletionMessageParam,
) -> None:
    """Append a single message to a conversation's history.

    Creates the conversation row if it doesn't already exist.
    """
    await append_messages(conversation_id, [message])


async def append_messages(
    conversation_id: str,
    messages: Sequence[ChatCompletionMessageParam],
) -> None:
    """Append multiple messages to a conversation's history.

    Creates the conversation row if it doesn't already exist.
    """
    _ensure_engine()
    from src.db.database import AsyncSessionLocal
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except (ValueError, AttributeError):
        return

    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        # Ensure the conversation row exists
        existing = await session.execute(
            select(Conversation.id).where(Conversation.id == conv_uuid)
        )
        if existing.scalar_one_or_none() is None:
            session.add(Conversation(id=conv_uuid))

        for msg in messages:
            session.add(
                Message(
                    conversation_id=conv_uuid,
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                )
            )
        await session.commit()


async def clear() -> None:
    """Delete all messages and conversations (useful for testing)."""
    _ensure_engine()
    from src.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        await session.execute(delete(Message))
        await session.execute(delete(Conversation))
        await session.commit()