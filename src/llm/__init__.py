from src.config import Settings
from src.llm.base import LLMProvider
from src.llm.ollama import OllamaProvider
from src.llm.openrouter import OpenRouterProvider


def get_llm_provider(settings: Settings) -> LLMProvider:
    """
    Factory: return the right LLM provider based on settings.llm_provider.
    Uses ollama as primary, falls back to openrouter if ollama fails
    (the fallback is handled by the caller, not here).
    """
    if settings.llm_provider == "ollama":
        return OllamaProvider(settings)
    elif settings.llm_provider == "openrouter":
        return OpenRouterProvider(settings)
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


# These names are available when someone does:
#   from src.llm import LLMProvider, get_llm_provider
__all__ = ["LLMProvider", "get_llm_provider"]