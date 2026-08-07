import json
import time
from collections.abc import Sequence

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from openai.types.chat import ChatCompletionMessageParam

from src.config import settings
from src.llm import get_llm_provider
from src.guard import check_prompt_injection, check_content_safety, check_pii_leak
from src.rate_limiter import limiterIp, limiterConv
from src.db.store import create_conversation, get_history, append_messages
from src.prompt import build_system_prompt, count_tokens_approx
from src.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])

_ERROR_MESSAGE = "I'm sorry, I encountered an error processing your request. Please try again."


def _refusal_message(guard: str) -> str:
    """Polite refusal for a blocked message (guard: 'prompt_injection' or 'content_safety')."""
    if guard == "prompt_injection":
        return (
            "I'm sorry, but I can't process that request. "
            f"Please ask a question about {settings.personal_name}'s professional background."
        )
    return (
        f"I'm here to answer questions about {settings.personal_name}'s professional experience. "
        "Please ask something related to his background, skills, or projects."
    )


def _count_prompt_tokens(
    system_prompt: str,
    conversation: Sequence[ChatCompletionMessageParam],
    user_message: str,
) -> tuple[int, int, int, int]:
    """Token counts (system, conversation, user, total) for logging."""
    system_tokens = count_tokens_approx(system_prompt)
    conversation_tokens = count_tokens_approx(
        " ".join(str(m.get("content", "")) for m in conversation)
    )
    user_message_tokens = count_tokens_approx(user_message)
    return (
        system_tokens,
        conversation_tokens,
        user_message_tokens,
        system_tokens + conversation_tokens + user_message_tokens,
    )


async def _save_and_scrub(conversation_id: str, user_message: str, assistant_text: str) -> str:
    """Persist the exchange and return the PII-scrubbed assistant text."""
    await append_messages(conversation_id, [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_text},
    ])
    return check_pii_leak(assistant_text)


@router.post("/chat", response_model=ChatResponse)
@limiterIp.limit(settings.rate_limit_per_ip)
@limiterConv.limit(settings.rate_limit_per_conversation)
async def chat(request: Request, body: ChatRequest):
    start_time = time.time()
    logger: structlog.stdlib.BoundLogger = request.state.logger

    # Resolve conversation ID — create one if the client didn't provide it
    conversation_id = request.headers.get("x-conversation-id") or await create_conversation()

    # Re-bind logger with the resolved conversation_id so all subsequent
    # log lines in this request carry the correct ID.
    logger = logger.bind(conversationId=conversation_id)

    logger.info("request_received", message_length=len(body.message))

    # 1. Guards: prompt injection + content safety
    for guard, check in (
        ("prompt_injection", check_prompt_injection),
        ("content_safety", check_content_safety),
    ):
        passed, reason = check(body.message)
        if not passed:
            logger.info("guard_check_blocked", check_type=guard, reason=reason)
            return ChatResponse(
                response=_refusal_message(guard),
                conversation_id=conversation_id,
            )

    logger.info("guard_check_passed")

    # 2. Retrieve conversation history from server-side store
    conversation = await get_history(conversation_id)

    # 3. Build system prompt from data files and send to LLM
    system_prompt = build_system_prompt()
    provider = get_llm_provider(settings)

    # Token accounting: system prompt, conversation history, and current user message
    system_tokens, conversation_tokens, user_message_tokens, total_prompt_tokens = (
        _count_prompt_tokens(system_prompt, conversation, body.message)
    )

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
        return ChatResponse(response=_ERROR_MESSAGE, conversation_id=conversation_id)

    llm_latency_ms = int((time.time() - start_time) * 1000)

    if response_text is None:
        logger.info("llm_call_complete", model=provider.model_name(), response_empty=True)
        return ChatResponse(response=_ERROR_MESSAGE, conversation_id=conversation_id)

    logger.info(
        "llm_call_complete",
        model=provider.model_name(),
        tokens_used=count_tokens_approx(response_text),
        latency_ms=llm_latency_ms,
    )

    # 4. Persist the exchange, then scrub PII from the response
    safe_response = await _save_and_scrub(conversation_id, body.message, response_text)

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


# ─── Streaming chat endpoint (Server-Sent Events) ───────────────────


def _sse_event(event: str, data: str) -> str:
    """Format a Server-Sent Events message.

    SSE spec: one or more `field: value` lines terminated by a blank line.
    Data lines with embedded newlines are split across multiple `data:` lines.
    """
    lines = data.split("\n")
    payload = "\n".join(f"data: {line}" for line in lines)
    return f"event: {event}\n{payload}\n\n"


def _sse_step(step_id: str, label: str, status: str) -> str:
    """Format a `step` SSE event describing pipeline progress.

    The client can render a progress indicator from these step events.
    `status` is typically "running" (step started) or "done" (step finished).
    """
    data = json.dumps({"step": step_id, "label": label, "status": status})
    return _sse_event("step", data)


@router.post("/chat/stream")
@limiterIp.limit(settings.rate_limit_per_ip)
@limiterConv.limit(settings.rate_limit_per_conversation)
async def chat_stream(request: Request, body: ChatRequest):
    """Stream LLM response as Server-Sent Events.

    Event types:
      - event: token    data: <chunk>     (zero or more, the actual content)
      - event: done     data: <full_text>  (once, when streaming is complete)
      - event: error    data: <message>   (once, on error)
      - event: blocked  data: <message>   (once, when guard check fails)
    """
    start_time = time.time()
    logger: structlog.stdlib.BoundLogger = request.state.logger

    conversation_id = request.headers.get("x-conversation-id") or await create_conversation()
    logger = logger.bind(conversationId=conversation_id)
    logger.info("request_received", message_length=len(body.message), streaming=True)

    async def event_generator():
        # 1. Guards: prompt injection + content safety
        yield _sse_step("checking_safety", "Checking question safety...", "running")

        for guard, check in (
            ("prompt_injection", check_prompt_injection),
            ("content_safety", check_content_safety),
        ):
            passed, reason = check(body.message)
            if not passed:
                logger.info("guard_check_blocked", check_type=guard, reason=reason)
                yield _sse_step("checking_safety", "Question blocked", "done")
                yield _sse_event("blocked", _refusal_message(guard))
                return

        logger.info("guard_check_passed")
        yield _sse_step("checking_safety", "Question passed safety check", "done")

        # 2. RAG retrieval: embed the query and search the vector store for
        # relevant context chunks. Failures here are non-fatal — we fall back
        # to generating without retrieved context.
        yield _sse_step("searching_kb", "Searching knowledge base...", "running")

        from src.rag.embedding import embed_text
        from src.rag.pipeline import search_similar

        similar_docs = []
        try:
            query_embedding = await embed_text(body.message)
            similar_docs = await search_similar(query_embedding, top_k=5)
        except Exception as e:
            logger.info(
                "rag_search_failed",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            similar_docs = []

        rag_context = "\n\n---\n\n".join(str(d.content) for d in similar_docs)
        logger.info("rag_search_complete", rag_chunks=len(similar_docs))
        yield _sse_step(
            "searching_kb",
            f"Found {len(similar_docs)} relevant context chunks",
            "done",
        )

        # 3. Build the system prompt with retrieved context and get provider
        yield _sse_step("building_prompt", "Building prompt...", "running")

        conversation = await get_history(conversation_id)
        system_prompt = build_system_prompt(rag_context)
        provider = get_llm_provider(settings)

        system_tokens, conversation_tokens, user_message_tokens, total_prompt_tokens = (
            _count_prompt_tokens(system_prompt, conversation, body.message)
        )

        logger.info(
            "llm_call_start",
            model=provider.model_name(),
            provider=settings.llm_provider,
            system_tokens=system_tokens,
            conversation_tokens=conversation_tokens,
            user_message_tokens=user_message_tokens,
            total_prompt_tokens=total_prompt_tokens,
            rag_chunks=len(similar_docs),
            streaming=True,
        )

        yield _sse_step(
            "building_prompt",
            f"Prompt ready ({total_prompt_tokens} tokens)",
            "done",
        )

        # 4. Stream tokens from the LLM provider
        yield _sse_step("generating", "Generating response...", "running")

        full_response = ""
        try:
            async for chunk in provider.chat_stream(
                systemPrompt=system_prompt,
                conversation=conversation,
                userMessage=body.message,
            ):
                full_response += chunk
                yield _sse_event("token", chunk)
        except Exception as e:
            logger.info(
                "llm_call_error",
                model=provider.model_name(),
                error_type=type(e).__name__,
                error_message=str(e),
            )
            yield _sse_step("generating", "Generation failed", "done")
            yield _sse_event("error", _ERROR_MESSAGE)
            return

        llm_latency_ms = int((time.time() - start_time) * 1000)

        if not full_response.strip():
            logger.info("llm_call_complete", model=provider.model_name(), response_empty=True)
            yield _sse_step("generating", "Generation failed", "done")
            yield _sse_event("error", _ERROR_MESSAGE)
            return

        logger.info(
            "llm_call_complete",
            model=provider.model_name(),
            tokens_used=count_tokens_approx(full_response),
            latency_ms=llm_latency_ms,
        )

        yield _sse_step("generating", "Response generated", "done")

        # 5. Persist the exchange, scrub PII, and send the final complete text
        yield _sse_step("saving", "Saving conversation...", "running")
        safe_response = await _save_and_scrub(conversation_id, body.message, full_response)
        yield _sse_step("saving", "Conversation saved", "done")

        total_latency_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "response_sent",
            answer_length=len(safe_response),
            total_latency_ms=total_latency_ms,
        )

        # Send the final complete response so the client can replace
        # the accumulated (possibly PII-bearing) text with the scrubbed version.
        yield _sse_event("done", safe_response)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable nginx buffering (Render uses nginx)
        },
    )
