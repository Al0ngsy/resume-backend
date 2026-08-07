from src.config import Settings
from src.llm.openai_compat import OpenAICompatProvider


def get_llm_provider(settings: Settings) -> OpenAICompatProvider:
    """Build the OpenAI-compatible client for the configured provider."""
    if settings.llm_provider == "ollama":
        return OpenAICompatProvider(
            name="ollama",
            base_url=settings.ollama_base_url,
            api_key=settings.ollama_api_key,
            model=settings.ollama_model,
            reasoning_effort=settings.ollama_reasoning_effort,
        )
    if settings.llm_provider == "openrouter":
        return OpenAICompatProvider(
            name="openrouter",
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            default_headers={
                "HTTP-Referer": "https://github.com/Al0ngsy/resume-backend",
                "X-Title": "Resume Chatbot",
            },
        )
    if settings.llm_provider == "opencode":
        return OpenAICompatProvider(
            name="opencode",
            base_url=settings.opencode_base_url,
            api_key=settings.opencode_api_key,
            model=settings.opencode_model,
            reasoning_effort=settings.opencode_reasoning_effort,
        )
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
