import pytest

from src.rag import pipeline


@pytest.mark.asyncio
async def test_reindex_all_delegates_to_reindex_source(monkeypatch):
    """reindex_all = reindex_source for every source, tolerating failures."""
    calls = []

    async def fake_reindex_source(source):
        calls.append(source)
        if source == "pdf_en":
            raise FileNotFoundError("pdf missing")
        return 7

    monkeypatch.setattr(pipeline, "reindex_source", fake_reindex_source)

    summary = await pipeline.reindex_all()

    assert calls == ["pdf_en", "pdf_de", "qa"]  # every source attempted, in order
    assert summary == {"pdf_de": 7, "qa": 7}  # failed source skipped, counts aggregated
