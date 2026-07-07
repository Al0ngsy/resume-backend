from collections.abc import Sequence

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from src.config import Settings
from src.llm.base import LLMProvider

class OllamaProvider(LLMProvider):
    """Implementation of the OpenAI Ollama model (local and cloud)."""

    def __init__(self, settings: Settings):
        # Local Ollama doesn't require auth, but the OpenAI SDK requires
        # a non-empty api_key string. Passing "ollama" as a dummy value
        # satisfies the SDK without needing a real key.
        self._client = OpenAI(
            api_key=settings.ollamaApiKey or 'ollama',
            base_url=settings.ollamaBaseUrl
        )
        self._model = settings.ollamaModel

    def model_name(self) -> str:
        return self._model
    
    async def chat(
          self, 
          systemPrompt: str,
          conversation: Sequence[ChatCompletionMessageParam], 
          userMessage: str
        ) -> str | None:
        """Send a chat request to Ollama and return the response text."""
        try:
          messages: list[ChatCompletionMessageParam] = [
              {"role": "system", "content": systemPrompt},
              *conversation,
              {"role": "user", "content": userMessage},
          ]
          response = self._client.chat.completions.create(
              model=self._model,
              messages=messages,
              temperature=0.7,
          )
          return response.choices[0].message.content or ''
        except Exception as e:
          print(f"Error oc_curred while sending chat request to Ollama: {e}")
