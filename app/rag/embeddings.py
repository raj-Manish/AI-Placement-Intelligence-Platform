"""
Embeddings module for AI Placement Intelligence Platform:
Generates dense vector embeddings using Google Gemini's embedding models.
Produces 768-dimensional vectors aligned with PostgreSQL pgvector schema.
"""

import os
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Standard embedding configuration
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"
EMBEDDING_DIM = 768


class EmbeddingError(Exception):
    """Custom exception raised when embedding generation fails."""
    pass


def _configure_genai():
    """Configures Google Generative AI SDK with API key from environment."""
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise EmbeddingError(
            "GOOGLE_API_KEY is not configured in your .env file.\n"
            "Please obtain a free API key from https://aistudio.google.com/ and add it to .env:\n"
            "GOOGLE_API_KEY=AIzaSy..."
        )
    genai.configure(api_key=api_key)


def embed_text(text: str) -> List[float]:
    """
    Generates a 768-dimensional embedding vector for a single query text.

    Args:
        text (str): Query string or chunk text.

    Returns:
        List[float]: 768-dimensional floating point embedding vector.
    """
    if not text or not text.strip():
        raise EmbeddingError("Cannot generate embedding for empty text.")

    _configure_genai()
    try:
        res = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=text.strip(),
            output_dimensionality=EMBEDDING_DIM
        )
        vector = res["embedding"]
        if len(vector) != EMBEDDING_DIM:
            raise EmbeddingError(
                f"Embedding dimension mismatch: expected {EMBEDDING_DIM}, got {len(vector)}"
            )
        return vector
    except EmbeddingError:
        raise
    except Exception as e:
        raise EmbeddingError(f"Gemini API embedding call failed: {str(e)}")


def embed_documents(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a batch of text chunks.

    Args:
        texts (List[str]): List of chunk texts.

    Returns:
        List[List[float]]: List of 768-dimensional embedding vectors.
    """
    if not texts:
        return []

    cleaned_texts = [t.strip() for t in texts if t and t.strip()]
    if not cleaned_texts:
        raise EmbeddingError("No valid non-empty texts to embed.")

    _configure_genai()
    try:
        res = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=cleaned_texts,
            output_dimensionality=EMBEDDING_DIM
        )
        vectors = res["embedding"]
        for i, vec in enumerate(vectors):
            if len(vec) != EMBEDDING_DIM:
                raise EmbeddingError(
                    f"Chunk {i} embedding dimension mismatch: expected {EMBEDDING_DIM}, got {len(vec)}"
                )
        return vectors
    except EmbeddingError:
        raise
    except Exception as e:
        raise EmbeddingError(f"Gemini batch embedding call failed: {str(e)}")
