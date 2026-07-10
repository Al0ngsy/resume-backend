import time

import structlog
from fastapi import APIRouter, Request

from src.config import settings
from src.llm import get_llm_provider
from src.guard import check_prompt_injection, check_content_safety, check_pii_leak
from src.rate_limiter import limiterIp, limiterConv
from src.conversation_store import create_conversation, get_history, append_messages
from src.prompt import build_system_prompt, count_tokens_approx
from src.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
@limiterIp.limit(settings.rate_limit_per_ip)
@limiterConv.limit(settings.rate_limit_per_conversation)
async def chat(request: Request, body: ChatRequest):
    start_time = time.time()
    logger: structlog.stdlib.BoundLogger = request.state.logger

    # Resolve conversation ID — create one if the client didn't provide it
    conversation_id = request.headers.get("x-conversation-id") or create_conversation()

    # Re-bind logger with the resolved conversation_id so all subsequent
    # log lines in this request carry the correct ID.
    logger = logger.bind(conversationId=conversation_id)

    logger.info("request_received", message_length=len(body.message))

    # 1. Guard: prompt injection check
    passed, reason = check_prompt_injection(body.message)
    if not passed:
        logger.info("guard_check_blocked", check_type="prompt_injection", reason=reason)
        return ChatResponse(
            response="I'm sorry, but I can't process that request. Please ask a question about Le Quoc Anh Tran's professional background.",
            conversation_id=conversation_id,
        )

    # 2. Guard: content safety / on-topic check
    passed, reason = check_content_safety(body.message)
    if not passed:
        logger.info("guard_check_blocked", check_type="content_safety", reason=reason)
        return ChatResponse(
            response="I'm here to answer questions about Le Quoc Anh Tran's professional experience. Please ask something related to his background, skills, or projects.",
            conversation_id=conversation_id,
        )

    logger.info("guard_check_passed")

    # 3. Retrieve conversation history from server-side store
    conversation = get_history(conversation_id)

    # 4. Build system prompt from data files and send to LLM
    system_prompt = build_system_prompt()
    provider = get_llm_provider(settings)

    # Token accounting: system prompt, conversation history, and current user message
    system_tokens = count_tokens_approx(system_prompt)
    conversation_tokens = count_tokens_approx(
        " ".join(str(m.get("content", "")) for m in conversation)
    )
    user_message_tokens = count_tokens_approx(body.message)
    total_prompt_tokens = system_tokens + conversation_tokens + user_message_tokens

    logger.info(
        "llm_call_start",
        model=provider.model_name(),
        provider=settings.llm_provider,
        system_tokens=system_tokens,
        conversation_tokens=conversation_tokens,
        user_message_tokens=user_message_tokens,
        total_prompt_tokens=total_prompt_tokens,
    )

    try:
        response_text = await provider.chat(
            systemPrompt=system_prompt,
            conversation=conversation,
            userMessage=body.message,
        )
    except Exception as e:
        logger.info(
            "llm_call_error",
            model=provider.model_name(),
            error_type=type(e).__name__,
            error_message=str(e),
        )
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request. Please try again.",
            conversation_id=conversation_id,
        )

    llm_latency_ms = int((time.time() - start_time) * 1000)

    if response_text is None:
        logger.info("llm_call_complete", model=provider.model_name(), response_empty=True)
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request. Please try again.",
            conversation_id=conversation_id,
        )

    logger.info(
        "llm_call_complete",
        model=provider.model_name(),
        tokens_used=count_tokens_approx(response_text),
        latency_ms=llm_latency_ms,
    )

    # 5. Persist the exchange to the store
    append_messages(conversation_id, [
        {"role": "user", "content": body.message},
        {"role": "assistant", "content": response_text},
    ])

    # 6. Scrub PII from response
    safe_response = check_pii_leak(response_text)

    total_latency_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "response_sent",
        answer_length=len(safe_response),
        total_latency_ms=total_latency_ms,
    )

    return ChatResponse(
        response=safe_response,
        conversation_id=conversation_id,
    )
