from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Sequence
from openai.types.chat import ChatCompletionMessageParam

class LLMProvider(ABC):
    """Every LLM provider must implement this."""

    @abstractmethod
    async def chat(
        self, 
        systemPrompt: str, 
        conversation: Sequence[ChatCompletionMessageParam], 
        userMessage: str
      ) -> str | None:
        """Send a chat request and return the response text."""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        systemPrompt: str,
        conversation: Sequence[ChatCompletionMessageParam],
        userMessage: str,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response token by token.

        Yields content deltas as they arrive from the LLM.
        The caller is responsible for accumulating the full text.
        """
        ...
        # pragma: no cover — abstract method
        yield ""  # type: ignore[unreachable]  # makes this an async generator

    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier (e.g. 'llama3.2', 'deepseek-chat')."""
        ...
