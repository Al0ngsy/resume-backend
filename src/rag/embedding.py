"""
Embedding service backed by Jina AI (OpenAI-compatible API).

Creates the AsyncOpenAI client lazily so that importing this module does not
require configured credentials — mirroring the lazy-engine pattern in
src/database.py. Exposes two helpers:
  - embed_text(text)  -> single embedding
  - embed_batch(texts) -> batch of embeddings (up to 2048 inputs per request)
"""
from openai import AsyncOpenAI

from src.config import settings
from src.logging_config import getLogger

_log = getLogger(__name__)

# Lazy client — constructed on first use so importing this module does not
# require EMBEDDING_API_KEY to be set (matches the lazy pattern used by the LLM
# providers in src/llm/, and keeps test collection / tooling import-safe).
_client: AsyncOpenAI | None = None


def _ensure_client() -> AsyncOpenAI:
    """Create the AsyncOpenAI client on first use."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url,
        )
    return _client


async def embed_text(text: str) -> list[float]:
    """Return the embedding for a single text input."""
    client = _ensure_client()
    try:
        resp = await client.embeddings.create(
            model=settings.embedding_model,
            input=text,
        )
        return resp.data[0].embedding
    except Exception as e:
        _log.error(
            "embed_text_failed",
            model=settings.embedding_model,
            error_type=type(e).__name__,
            error_message=str(e),
        )
        raise


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Return embeddings for a batch of texts.

    Jina API supports batch inputs. Caller is responsible for
    chunking larger lists.
    """
    if not texts:
        return []
    client = _ensure_client()
    try:
        resp = await client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )
        return [d.embedding for d in sorted(resp.data, key=lambda x: x.index)]
    except Exception as e:
        _log.error(
            "embed_batch_failed",
            model=settings.embedding_model,
            batch_size=len(texts),
            error_type=type(e).__name__,
            error_message=str(e),
        )
        raise