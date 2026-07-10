from collections.abc import Sequence

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import Settings
from src.llm.base import LLMProvider
from src.logging_config import getLogger

_log = getLogger(__name__)


class OpenRouterProvider(LLMProvider):
    """LLM provider for OpenRouter (any model, fallback)."""

    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/Al0ngsy/resume-backend",
                "X-Title": "Resume Chatbot",
            },
        )
        self._model = settings.openrouter_model

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
                "openrouter_call_failed",
                model=self._model,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise RuntimeError(f"OpenRouter call failed: {e}") from e
