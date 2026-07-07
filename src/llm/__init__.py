from src.config import Settings
from src.llm.base import LLMProvider
from src.llm.ollama import OllamaProvider
# from src.llm.deepseek import DeepSeekProvider
# from src.llm.openrouter import OpenRouterProvider

def get_llm_provider(settings: Settings) -> LLMProvider:
    """Factory: return the right LLM provider based on settings.llmProvider."""
    if settings.llmProvider == "ollama":
        return OllamaProvider(settings)
    # TODO: Add more providers if needed
    # elif settings.llmProvider == "deepseek":
    #     return DeepSeekProvider(settings)
    # elif settings.llmProvider == "openrouter":
    #     return OpenRouterProvider(settings)
    raise ValueError(f"Unknown LLM provider: {settings.llmProvider}")


# These names are available when someone does:
# from src.llm import LLMProvider, get_llm_provider
__all__ = ["LLMProvider", "get_llm_provider"]