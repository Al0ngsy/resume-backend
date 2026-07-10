import structlog
from fastapi import APIRouter, Request
from pydantic import BaseModel
from openai.types.chat import ChatCompletionMessageParam

from src.config import settings
from src.llm import get_llm_provider
from src.guard import check_prompt_injection, check_content_safety, check_pii_leak
from src.rate_limiter import limiterIp, limiterConv
from src.conversation_store import create_conversation, get_history, append_messages
from src.prompt import build_system_prompt

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    # history is no longer accepted from the client — the server manages it
    # via x-conversation-id. Kept as an optional field for backward compatibility
    # but will be ignored.

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@router.post("/chat", response_model=ChatResponse)
@limiterIp.limit(settings.rateLimitPerIp)
@limiterConv.limit(settings.rateLimitPerConversation)
async def chat(request: Request, body: ChatRequest):
    logger: structlog.stdlib.BoundLogger = request.state.logger

    # Resolve conversation ID — create one if the client didn't provide it
    conversation_id = request.headers.get("x-conversation-id") or create_conversation()

    # 1. Guard: prompt injection check
    passed, reason = check_prompt_injection(body.message)
    if not passed:
        logger.error(error=reason)
        return ChatResponse(
            response="I'm sorry, but I can't process that request. Please ask a question about Le Quoc Anh Tran's professional background.",
            conversation_id=conversation_id,
        )

    # 2. Guard: content safety / on-topic check
    passed, reason = check_content_safety(body.message)
    if not passed:
        logger.error(error=reason)
        return ChatResponse(
            response="I'm here to answer questions about Le Quoc Anh Tran's professional experience. Please ask something related to his background, skills, or projects.",
            conversation_id=conversation_id,
        )

    # 3. Retrieve conversation history from server-side store
    conversation: list[ChatCompletionMessageParam] = get_history(conversation_id)

    # 4. Build system prompt from data files and send to LLM
    system_prompt = build_system_prompt()
    provider = get_llm_provider(settings)
    response_text = await provider.chat(
        systemPrompt=system_prompt,
        conversation=conversation,
        userMessage=body.message,
    )

    if response_text is None:
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request. Please try again.",
            conversation_id=conversation_id,
        )

    # 5. Persist the exchange to the store
    append_messages(conversation_id, [
        {"role": "user", "content": body.message},
        {"role": "assistant", "content": response_text},
    ])

    # 6. Scrub PII from response
    safe_response = check_pii_leak(response_text)

    return ChatResponse(
        response=safe_response,
        conversation_id=conversation_id,
    )
