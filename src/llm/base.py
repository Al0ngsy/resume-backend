from abc import ABC, abstractmethod
from collections.abc import Sequence
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
    def model_name(self) -> str:
        """Return the model identifier (e.g. 'llama3.2', 'deepseek-chat')."""
        ...
