"""Text chunking for documents and Q&A pairs."""
from typing import Any

import tiktoken

CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50

# cl100k_base is the encoding used by OpenAI's text-embedding-3-* models.
_encoding = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, source: str) -> list[dict[str, Any]]:
    """Split text into overlapping chunks of CHUNK_SIZE_TOKENS tokens.

    Returns a list of dicts with keys: content, source, chunk_index, metadata.
    metadata contains token_start, token_end, char_count.
    """
    tokens = _encoding.encode(text)
    if not tokens:
        return []

    chunks: list[dict[str, Any]] = []
    step = CHUNK_SIZE_TOKENS - CHUNK_OVERLAP_TOKENS
    token_start = 0
    chunk_index = 0

    while token_start < len(tokens):
        token_end = min(token_start + CHUNK_SIZE_TOKENS, len(tokens))
        chunk_tokens = tokens[token_start:token_end]
        chunk_content = _encoding.decode(chunk_tokens)
        chunks.append(
            {
                "content": chunk_content,
                "source": source,
                "chunk_index": chunk_index,
                "metadata": {
                    "token_start": token_start,
                    "token_end": token_end,
                    "char_count": len(chunk_content),
                },
            }
        )
        chunk_index += 1
        if token_end == len(tokens):
            break
        token_start += step

    return chunks


def chunk_qa_pairs(qa_data: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Convert Q&A pairs into one chunk each.

    Each qa_data item should have 'question' and 'answer' keys.
    Returns a list of dicts with keys: content, source, chunk_index, metadata.
    """
    chunks: list[dict[str, Any]] = []
    for i, qa in enumerate(qa_data):
        question = qa.get("question", "")
        answer = qa.get("answer", "")
        content = f"Q: {question}\nA: {answer}"
        chunks.append(
            {
                "content": content,
                "source": "qa",
                "chunk_index": i,
                "metadata": {"question": question},
            }
        )
    return chunks