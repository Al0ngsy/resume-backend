import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest_asyncio.fixture
async def client():
    """An async HTTP client that talks to the app directly (no network)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
def mock_llm_provider():
    """A fake LLM provider that returns canned responses."""
    from unittest.mock import AsyncMock, MagicMock

    mock = MagicMock()
    mock.chat = AsyncMock(return_value="This is a mock response about Anh's skills.")
    mock.model_name.return_value = "mock-model"
    return mock
