"""ORM models for conversations, messages, and document chunks."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from pgvector.sqlalchemy import Vector

from src.db.database import Base


def _now() -> datetime:
    """Timezone-aware UTC now, used as default for datetime columns."""
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1024), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    __table_args__ = (
        Index(
            "ix_documents_embedding_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )