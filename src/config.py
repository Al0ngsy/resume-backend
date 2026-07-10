from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
  # `pydantic-settings` automatically reads the `.env` file and maps each line to a class field by name
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

  # tries these variants in order when looking for a env-var match 
  # - The exact field name: `llmProvider`
  # - Uppercase version: `LLMPROVIDER`
  # - Snake_case uppercase: `LLM_PROVIDER`
  # first matching variant is used, if none match, the default value is used
  llmProvider: str = "ollama"

  # Ollama settings
  ollamaBaseUrl: str = "http://localhost:11434/v1"
  ollamaApiKey: str = "" # local models does not require an API key, only if using Ollama Cloud
  ollamaModel: str = "ornith:latest" 

  # DeepSeek settings -- fallback on ollama
  deepseekApiKey: str = ""
  deepseekBaseUrl: str = "https://api.deepseek.com/v1"
  deepseekModel: str = ""

  # OpenRouter settings -- fallback on ollama
  openRouterApiKey: str = ""
  openRouterBaseUrl: str = "https://openrouter.ai/api/v1"
  openRouterModel: str = ""

  # Rate limiting
  rateLimitPerIp: str = "3/minute" # 3 requests per minute per IP address
  rateLimitPerConversation: str = "12/day" # 12 request per conversation per day, afterwards the recruiter is prompted to contact directy instead

  # CORS
  corsOrigins: str = "http://localhost:3000"

  # PII allowlist (comma-separated) — these emails/phones won't be redacted
  allowedEmails: str = ""
  allowedPhones: str = ""

  # Logging
  logLevel: str = "info"

  # Personal info (used in prompt builder — override in .env for different profiles)
  personalName: str = "Le Quoc Anh Tran"
  personalEmail: str = "lequocanhtr@gmail.com"
  personalGithub: str = "https://github.com/Al0ngsy"
  personalLinkedin: str = "https://linkedin.com/in/lequocanhtr"
  personalTitle: str = "Backend Software Engineer"

  # ─── Startup validation ─────────────────────────────────────────────
  @model_validator(mode="after")
  def validate_provider_config(self):
    if self.llmProvider == "deepseek" and not self.deepseekApiKey:
      raise ValueError(
        "DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek.\n"
        "  Either set DEEPSEEK_API_KEY in your .env file,\n"
        "  or change LLM_PROVIDER to 'ollama'."
      )
    if self.llmProvider == "openrouter" and not self.openRouterApiKey:
      raise ValueError(
        "OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter.\n"
        "  Either set OPENROUTER_API_KEY in your .env file,\n"
        "  or change LLM_PROVIDER to 'ollama'."
      )
    return self

# this run once when module is imported for the first time, and the settings are cached for subsequent imports
settings = Settings()
