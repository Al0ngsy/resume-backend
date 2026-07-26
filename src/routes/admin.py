"""Admin endpoints: re-indexing and other maintenance operations."""
from fastapi import APIRouter, HTTPException, Request

from src.rag.pipeline import reindex_all, reindex_source
from src.rate_limiter import limiterIp

router = APIRouter(prefix="/api/admin", tags=["admin"])

VALID_SOURCES = ["pdf_en", "pdf_de", "qa"]


@router.post("/reindex")
@limiterIp.limit("5/day")
async def reindex(request: Request):
    """Rebuild the documents table from PDFs and the mock Q&A file.

    Without a `source` query parameter, this re-indexes ALL sources
    (deletes everything and re-embeds all chunks).

    With `?source=qa` (or `pdf_en`, `pdf_de`), only that source is
    re-indexed — other sources are left untouched. Use this when you
    only changed one file to avoid re-embedding everything.
    """
    source = request.query_params.get("source")

    if source:
        if source not in VALID_SOURCES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source: {source!r}. Must be one of: {', '.join(VALID_SOURCES)}",
            )
        try:
            count = await reindex_source(source)
            return {
                "status": "ok",
                "message": f"Re-indexed source '{source}'",
                "source": source,
                "chunks": count,
            }
        except (FileNotFoundError, ValueError) as e:
            raise HTTPException(status_code=400, detail=str(e))

    summary = await reindex_all()
    return {
        "status": "ok",
        "message": "Re-indexing complete",
        "summary": summary,
    }