from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from src.config import settings


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description=f"The recruiter's question about {settings.personal_name}",
        examples=["What is his strongest programming language?"],
    )


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
