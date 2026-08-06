from collections.abc import AsyncGenerator, Sequence
from typing import Literal

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import Settings
from src.llm.base import LLMProvider
from src.logging_config import getLogger

_log = getLogger(__name__)


class OpenCodeProvider(LLMProvider):
    """LLM provider for OpenCode Go — a low-cost subscription service.

    OpenAI-compatible endpoint (https://opencode.ai/zen/go/v1) serving a
    curated set of coding models (deepseek-v4-*, kimi-k2.*, glm-5.*, etc.).
    """

    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(
            api_key=settings.opencode_api_key,
            base_url=settings.opencode_base_url,
        )
        self._model = settings.opencode_model
        self._reasoning_effort: Literal["none", "low", "medium", "high"] = (
            settings.opencode_reasoning_effort
        )

    def model_name(self) -> str:
        return self._model

    async def chat(
        self,
        systemPrompt: str,
        conversation: Sequence[ChatCompletionMessageParam],
        userMessage: str,
    ) -> str | None:
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": systemPrompt},
                *conversation,
                {"role": "user", "content": userMessage},
            ]
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.5,
                reasoning_effort=self._reasoning_effort
            )
            return response.choices[0].message.content
        except Exception as e:
            _log.error(
                "opencode_call_failed",
                model=self._model,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise RuntimeError(f"OpenCode call failed: {e}") from e

    async def chat_stream(
        self,
        systemPrompt: str,
        conversation: Sequence[ChatCompletionMessageParam],
        userMessage: str,
    ) -> AsyncGenerator[str, None]:
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": systemPrompt},
                *conversation,
                {"role": "user", "content": userMessage},
            ]
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.5,
                stream=True,
                reasoning_effort=self._reasoning_effort

            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            _log.error(
                "opencode_stream_failed",
                model=self._model,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise RuntimeError(f"OpenCode stream failed: {e}") from e
