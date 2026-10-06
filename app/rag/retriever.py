"""
Retriever module for AI Placement Intelligence Platform:
Retrieves the most semantically relevant chunks from pgvector for a given candidate query.
Provides deduplication, page tracking, and threshold filtering.
"""

from typing import List, Dict, Any, Optional
from app.rag.vector_store import similarity_search, VectorStoreError


class RetrievalError(Exception):
    """Custom exception raised when context retrieval fails."""
    pass


def retrieve_context(
    query: str,
    top_k: int = 4,
    company_name: Optional[str] = None,
    min_similarity: float = 0.30
) -> List[Dict[str, Any]]:
    """
    Retrieves top-k relevant chunks from pgvector for a given candidate question.

    Args:
        query (str): The candidate's question.
        top_k (int): Number of top chunks to retrieve (default: 4).
        company_name (Optional[str]): Target company to restrict search to.
        min_similarity (float): Minimum cosine similarity threshold (0.0 to 1.0).

    Returns:
        List[Dict[str, Any]]: Filtered list of relevant chunks with page citations and text.
    """
    if not query or not query.strip():
        return []

    try:
        raw_chunks = similarity_search(
            query=query.strip(),
            top_k=top_k,
            company_name=company_name
        )

        # Filter out chunks that do not meet the minimum similarity threshold
        filtered_chunks = [
            c for c in raw_chunks
            if c.get("similarity_score", 0.0) >= min_similarity
        ]

        return filtered_chunks

    except VectorStoreError as e:
        raise RetrievalError(f"Vector retrieval failed: {str(e)}")
    except Exception as e:
        raise RetrievalError(f"Unexpected retrieval error: {str(e)}")


def format_context_for_prompt(chunks: List[Dict[str, Any]]) -> str:
    """
    Formats retrieved chunks into a clean, annotated context block for the LLM prompt.
    Each chunk is explicitly labeled with its filename and page number.
    """
    if not chunks:
        return "No relevant job description text found."

    context_blocks = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source_filename", "JD.pdf")
        page = chunk.get("page_number", 1)
        text = chunk.get("chunk_text", "").strip()

        block = f"--- [EXCERPT {i} | File: {source} | Page: {page}] ---\n{text}"
        context_blocks.append(block)

    return "\n\n".join(context_blocks)
