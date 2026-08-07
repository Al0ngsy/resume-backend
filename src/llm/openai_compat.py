"""One OpenAI-compatible LLM provider for ollama, openrouter, and opencode.

All three endpoints speak the OpenAI chat-completions protocol; only the
client configuration (base URL, key, model, headers, reasoning effort)
differs. A single class covers them — see get_llm_provider in __init__.py.
"""
from collections.abc import AsyncGenerator, Sequence
from typing import Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.logging_config import getLogger

_log = getLogger(__name__)


class OpenAICompatProvider:
    """Chat completions against any OpenAI-compatible endpoint."""

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        model: str,
        reasoning_effort: str | None = None,
        default_headers: dict[str, str] | None = None,
    ):
        self._name = name
        self._model = model
        self._reasoning_effort = reasoning_effort
        self._client = AsyncOpenAI(
            api_key=api_key or "ollama",
            base_url=base_url,
            default_headers=default_headers,
        )

    def model_name(self) -> str:
        return self._model

    def _messages(
        self,
        systemPrompt: str,
        conversation: Sequence[ChatCompletionMessageParam],
        userMessage: str,
    ) -> list[ChatCompletionMessageParam]:
        return [
            {"role": "system", "content": systemPrompt},
            *conversation,
            {"role": "user", "content": userMessage},
        ]

    async def chat(
        self,
        systemPrompt: str,
        conversation: Sequence[ChatCompletionMessageParam],
        userMessage: str,
    ) -> str | None:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=self._messages(systemPrompt, conversation, userMessage),
                temperature=0.5,
                **self._extra_kwargs(),
            )
            return response.choices[0].message.content
        except Exception as e:
            _log.error(
                "llm_call_failed",
                provider=self._name,
                model=self._model,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise RuntimeError(f"{self._name} call failed: {e}") from e

    async def chat_stream(
        self,
        systemPrompt: str,
        conversation: Sequence[ChatCompletionMessageParam],
        userMessage: str,
    ) -> AsyncGenerator[str, None]:
        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=self._messages(systemPrompt, conversation, userMessage),
                temperature=0.5,
                stream=True,
                **self._extra_kwargs(),
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            _log.error(
                "llm_stream_failed",
                provider=self._name,
                model=self._model,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise RuntimeError(f"{self._name} stream failed: {e}") from e

    def _extra_kwargs(self) -> dict[str, Any]:
        if self._reasoning_effort is not None:
            return {"reasoning_effort": self._reasoning_effort}
        return {}
