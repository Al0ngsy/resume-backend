import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.config import settings


@pytest_asyncio.fixture
async def client():
    """An async HTTP client that talks to the app directly (no network).

    Auth is disabled during tests by clearing the API key.
    Rate limiter state is reset between tests to avoid cross-test interference.

    If a DB is configured AND reachable, routes use the real DB-backed store.
    Otherwise (no URL, sync-only URL, or connection failure) the conversation
    store is swapped for an async in-memory fake so endpoints still work.
    """
    from src.rate_limiter import limiterIp, limiterConv

    original_key = settings.api_key
    settings.api_key = ""
    limiterIp.reset()
    limiterConv.reset()

    store_patcher = None
    if not await _db_available():
        store_patcher = _patch_store(_FakeStore())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    if store_patcher is not None:
        store_patcher.stop()
    settings.api_key = original_key


@pytest_asyncio.fixture
def mock_llm_provider():
    """A fake LLM provider that returns canned responses."""
    from unittest.mock import AsyncMock, MagicMock

    mock = MagicMock()
    mock.chat = AsyncMock(return_value="This is a mock response about Anh's skills.")
    mock.model_name.return_value = "mock-model"
    return mock


@pytest_asyncio.fixture(autouse=True)
async def clear_db_if_configured():
    """Clear the DB between tests, but only if a usable DB is configured.

    No-op when the DB is unreachable so non-DB tests are unaffected.
    """
    if await _db_available():
        from src.db.store import clear
        await clear()


# ─── DB availability check ──────────────────────────────────────────────


async def _db_available() -> bool:
    """Return True if a DB URL is set AND a connection succeeds.

    Handles missing URL, sync-only URLs, and unreachable hosts by returning
    False so callers fall back to the in-memory fake store.
    """
    url = settings.database_url
    if not url:
        return False
    # create_async_engine needs an async driver; postgresql:// uses psycopg2
    # which may not be installed. Normalise to asyncpg.
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        engine = create_async_engine(url, pool_pre_ping=True)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        finally:
            await engine.dispose()
    except Exception:
        return False


# ─── In-memory async fake store (used when no DB is reachable) ─────────


class _FakeStore:
    """Async in-memory replacement matching conversation_store's API.

    Mirrors the old dict-backed store so existing tests pass without a live
    database. Implements every function the route code calls.
    """
    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, str]]] = {}

    async def create_conversation(self) -> str:
        import uuid
        conv_id = str(uuid.uuid4())
        self._store[conv_id] = []
        return conv_id

    async def conversation_exists(self, conversation_id: str) -> bool:
        return conversation_id in self._store

    async def get_history(self, conversation_id: str) -> list[dict[str, str]]:
        return list(self._store.get(conversation_id, []))

    async def append_messages(
        self, conversation_id: str, messages: list[dict[str, str]]
    ) -> None:
        self._store.setdefault(conversation_id, []).extend(messages)

    async def clear(self) -> None:
        self._store.clear()


def _patch_store(fake: "_FakeStore"):
    """Patch the conversation store names imported by the route modules.

    Patches call-site bindings in src.routes.chat and src.routes.conversations
    so the routes use the fake without touching production code. Only names
    actually imported by each module are patched.
    """
    from unittest.mock import patch

    # src.routes.chat imports: create_conversation, get_history, append_messages
    # src.routes.conversations imports: create_conversation, get_history, conversation_exists
    chat_funcs = ["create_conversation", "get_history", "append_messages"]
    conv_funcs = ["create_conversation", "get_history", "conversation_exists"]

    patches = []
    for fn in chat_funcs:
        patches.append(patch(f"src.routes.chat.{fn}", new=getattr(fake, fn)))
    for fn in conv_funcs:
        patches.append(patch(f"src.routes.conversations.{fn}", new=getattr(fake, fn)))
    for p in patches:
        p.start()
    return _Patcher(patches)


class _Patcher:
    """Stop all started patches on teardown."""
    def __init__(self, patches):
        self._patches = patches

    def stop(self):
        for p in reversed(self._patches):
            p.stop()