from collections.abc import AsyncGenerator, Sequence

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import Settings
from src.llm.base import LLMProvider
from src.logging_config import getLogger

_log = getLogger(__name__)


class OllamaProvider(LLMProvider):
    """
    LLM provider for Ollama (local or cloud).
    Thinking/reasoning output (e.g. <think> tags from deepseek-r1)
    is suppressed by passing appropriate extra_body options.
    """

    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(
            api_key=settings.ollama_api_key or "ollama",
            base_url=settings.ollama_base_url,
        )
        self._model = settings.ollama_model

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
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            _log.error(
                "ollama_call_failed",
                model=self._model,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise RuntimeError(f"Ollama call failed: {e}") from e

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
                temperature=0.7,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            _log.error(
                "ollama_stream_failed",
                model=self._model,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise RuntimeError(f"Ollama stream failed: {e}") from e