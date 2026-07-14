from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    # `pydantic-settings` automatically reads the `.env` file and maps each line to a class field by name
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # tries these variants in order when looking for a env-var match
    # - The exact field name: `llm_provider`
    # - Uppercase version: `llm_provider`
    # - Snake_case uppercase: `LLM_PROVIDER`
    # first matching variant is used, if none match, the default value is used
    llm_provider: str = "ollama"

    # Ollama settings
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_api_key: str = ""  # local models does not require an API key, only if using Ollama Cloud
    ollama_model: str = "ornith:latest"

    # OpenRouter settings -- fallback on ollama
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = ""

    # Rate limiting
    rate_limit_per_ip: str = "3/minute"  # 3 requests per minute per IP address
    rate_limit_per_conversation: str = "12/day"  # 12 request per conversation per day, afterwards the recruiter is prompted to contact directy instead

    # CORS
    cors_origins: str = "http://localhost:3000"

    # API key for frontend authentication (shared secret)
    # If empty, auth is disabled (local dev only)
    api_key: str = ""

    # PII allowlist (comma-separated) — these emails/phones won't be redacted
    allowed_emails: str = ""
    allowed_phones: str = ""

    # Logging
    log_level: str = "info"

    # Personal info (used in prompt builder — override in .env for different profiles)
    personal_name: str = ""
    personal_email: str = ""
    personal_github: str = ""
    personal_linkedin: str = ""
    personal_title: str = ""

    # ─── Startup validation ─────────────────────────────────────────────
    @model_validator(mode="after")
    def validate_provider_config(self):
        if self.llm_provider == "openrouter" and not self.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter.\n"
                "  Either set OPENROUTER_API_KEY in your .env file,\n"
                "  or change LLM_PROVIDER to 'ollama'."
            )
        return self


# this run once when module is imported for the first time, and the settings are cached for subsequent imports
settings = Settings()