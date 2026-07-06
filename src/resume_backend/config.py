from pydantic_settings import BaseSettings, SettingsConfigDict

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

  # Rate limiting
  rateLimitPerIp: str = "3/minute" # 3 requests per minute per IP address
  rateLimitPerConversation: str = "12" # 12 request per conversation, afterwards the recruiter is prompted to contact me instead

  # CORS
  corsOrigins: str = "http://localhost:3000"

  # Logging
  logLevel: str = "info"

# this run once when module is imported for the first time, and the settings are cached for subsequent imports
settings = Settings()