"""RAG pipeline: PDF/QA ingestion, embedding, and similarity search.

Builds and refreshes the `documents` table used by the retrieval-augmented
chat flow. PDFs are extracted with PyMuPDF (fitz), Q&A pairs are loaded from a
JSON file, both are chunked, embedded, and stored as `Document` rows with
pgvector embeddings. Similarity search uses cosine distance over the HNSW index.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
from sqlalchemy import delete, text

from src.rag.chunker import chunk_qa_pairs, chunk_text
from src.db.database import _ensure_engine
from src.db.models import Document
from src.rag.embedding import embed_batch
from src.logging_config import getLogger

_log = getLogger(__name__)

# Project layout (resume-backend/src/rag/pipeline.py):
#   project_root = .../resume-backend
#   PDF_DIR     = .../resume/resume-frontend/public
#   DATA_DIR    = .../resume-backend/data
project_root = Path(__file__).resolve().parent.parent.parent
PDF_DIR = project_root.parent / "resume-frontend" / "public"
DATA_DIR = project_root / "data"

PDF_FILES = {
    "pdf_en": PDF_DIR / "lequocanh_tran_cv_en.pdf",
    "pdf_de": PDF_DIR / "lequocanh_tran_cv_de.pdf",
}
QA_PATH = DATA_DIR / "mock-qa.json"


def _extract_pdf_text(pdf_path: Path) -> str:
    """Extract concatenated text from all pages of a PDF using PyMuPDF."""
    text_parts: list[str] = []
    doc = fitz.open(str(pdf_path))
    try:
        for page in doc:
            text_parts.append(str(page.get_text()))
    finally:
        doc.close()
    return "".join(text_parts)


async def reindex_all() -> dict[str, int]:
    """Rebuild the documents table from PDFs and the mock Q&A file.

    Steps:
      1. Delete all existing Document rows.
      2. Extract + chunk each PDF source.
      3. Load + chunk the Q&A pairs.
      4. Batch-embed all chunk contents.
      5. Insert Document rows with embeddings and commit.
    Returns a summary mapping source key to number of chunks ingested.
    """
    _log.info("reindex_start")
    _ensure_engine()
    from src.db.database import AsyncSessionLocal

    all_chunks: list[dict[str, Any]] = []
    summary: dict[str, int] = {}

    # 1. PDF sources
    for source_key, pdf_path in PDF_FILES.items():
        if not pdf_path.exists():
            _log.warning("pdf_missing", source=source_key, path=str(pdf_path))
            continue
        _log.info("extracting_pdf", source=source_key, path=str(pdf_path))
        text = _extract_pdf_text(pdf_path)
        if not text.strip():
            _log.warning("pdf_empty_text", source=source_key, path=str(pdf_path))
            continue
        chunks = chunk_text(text, source_key)
        all_chunks.extend(chunks)
        summary[source_key] = len(chunks)
        _log.info("chunked_pdf", source=source_key, chunks=len(chunks))

    # 2. Q&A source
    if QA_PATH.exists():
        _log.info("loading_qa", path=str(QA_PATH))
        with open(QA_PATH, "r", encoding="utf-8") as f:
            qa_data = json.load(f)
        qa_chunks = chunk_qa_pairs(qa_data)
        all_chunks.extend(qa_chunks)
        summary["qa"] = len(qa_chunks)
        _log.info("chunked_qa", chunks=len(qa_chunks))
    else:
        _log.warning("qa_missing", path=str(QA_PATH))

    if not all_chunks:
        _log.warning("reindex_no_chunks")
        return summary

    # 3. Batch-embed all chunk contents
    texts = [c["content"] for c in all_chunks]
    _log.info("embedding_chunks", count=len(texts))
    embeddings = await embed_batch(texts)
    if len(embeddings) != len(all_chunks):
        raise RuntimeError(
            f"Embedding count mismatch: got {len(embeddings)} for "
            f"{len(all_chunks)} chunks"
        )

    # 4. Build Document rows
    documents: list[Document] = []
    for chunk, emb in zip(all_chunks, embeddings):
        documents.append(
            Document(
                source=chunk["source"],
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                embedding=emb,
                metadata_=chunk.get("metadata"),
            )
        )

    # 5. Persist: delete old rows, insert new, commit
    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        await session.execute(delete(Document))
        _log.info("deleted_old_documents")
        session.add_all(documents)
        await session.commit()
        _log.info("inserted_documents", count=len(documents))

    _log.info("reindex_complete", summary=summary)
    return summary


async def reindex_source(source: str) -> int:
    """Re-embed a single source only (incremental reindex).

    Deletes only the rows matching `source` from the documents table,
    re-extracts/chunks/ embeds that source, and inserts the new rows.
    Unchanged sources are left untouched — saving embedding API calls.

    Args:
        source: One of "pdf_en", "pdf_de", "qa".

    Returns:
        Number of chunks re-indexed for that source.
    """
    _log.info("reindex_source_start", source=source)
    _ensure_engine()
    from src.db.database import AsyncSessionLocal

    all_chunks: list[dict[str, Any]] = []

    if source in PDF_FILES:
        pdf_path = PDF_FILES[source]
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        _log.info("extracting_pdf", source=source, path=str(pdf_path))
        text = _extract_pdf_text(pdf_path)
        if not text.strip():
            raise ValueError(f"PDF has no extractable text: {pdf_path}")
        all_chunks = chunk_text(text, source)

    elif source == "qa":
        if not QA_PATH.exists():
            raise FileNotFoundError(f"Q&A file not found: {QA_PATH}")
        _log.info("loading_qa", path=str(QA_PATH))
        with open(QA_PATH, "r", encoding="utf-8") as f:
            qa_data = json.load(f)
        all_chunks = chunk_qa_pairs(qa_data)

    else:
        raise ValueError(
            f"Unknown source: {source!r}. Must be one of: {', '.join(list(PDF_FILES) + ['qa'])}"
        )

    if not all_chunks:
        _log.warning("reindex_source_no_chunks", source=source)
        return 0

    # Batch-embed only this source's chunks
    texts = [c["content"] for c in all_chunks]
    _log.info("embedding_chunks", source=source, count=len(texts))
    embeddings = await embed_batch(texts)
    if len(embeddings) != len(all_chunks):
        raise RuntimeError(
            f"Embedding count mismatch: got {len(embeddings)} for "
            f"{len(all_chunks)} chunks (source={source})"
        )

    documents: list[Document] = []
    for chunk, emb in zip(all_chunks, embeddings):
        documents.append(
            Document(
                source=chunk["source"],
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                embedding=emb,
                metadata_=chunk.get("metadata"),
            )
        )

    # Delete only rows for this source, then insert new ones
    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        await session.execute(delete(Document).where(Document.source == source))
        _log.info("deleted_source_documents", source=source)
        session.add_all(documents)
        await session.commit()
        _log.info("inserted_source_documents", source=source, count=len(documents))

    _log.info("reindex_source_complete", source=source, chunks=len(documents))
    return len(documents)


async def search_similar(
    query_embedding: list[float],
    top_k: int = 5,
    max_distance: float = 0.5,
) -> list[Document]:
    """Return the top-k most similar Document rows by cosine distance.

    Only chunks with cosine distance < max_distance are returned. This
    filters out low-relevance chunks that would inject noise and cause
    the LLM to hallucinate (e.g., a distant chunk mentioning "frontend"
    triggering Angular/Vue associations). With pgvector cosine_distance,
    distance ranges from 0 (identical) to 2 (opposite); 0.5 is a common
    practical threshold for relevance with 1024-dim Jina embeddings.
    """
    _ensure_engine()
    from src.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:  # type: ignore[misc]
        # Use a raw query to filter by distance in SQL — pgvector computes
        # cosine_distance natively and we avoid fetching irrelevant rows.
        # The :embedding param is cast to the vector type by SQLAlchemy.
        stmt = text("""
            SELECT id, source, chunk_index, content, metadata,
                   embedding,
                   embedding <=> CAST(:embedding AS vector) AS distance
            FROM documents
            WHERE (embedding <=> CAST(:embedding AS vector)) < :max_distance
            ORDER BY distance
            LIMIT :top_k
        """).bindparams(
            embedding=str(query_embedding),
            max_distance=max_distance,
            top_k=top_k,
        )
        result = await session.execute(stmt)
        rows = result.fetchall()

    # Reconstruct Document objects from raw rows
    documents = []
    for row in rows:
        documents.append(
            Document(
                id=row[0],
                source=row[1],
                chunk_index=row[2],
                content=row[3],
                metadata_=row[4],
                embedding=row[5],
            )
        )
    return documents