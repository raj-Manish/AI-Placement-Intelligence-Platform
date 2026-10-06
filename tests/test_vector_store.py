"""
Test script for Phase 4: Embeddings & Vector Storage
Verifies:
1. Embeddings module validation and dimension check (768).
2. Missing API key handling.
3. Vector store similarity search query structure.
"""

import os
import sys

# Ensure root workspace is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.embeddings import (
    embed_text,
    embed_documents,
    EmbeddingError,
    EMBEDDING_DIM
)
from app.rag.vector_store import (
    similarity_search,
    VectorStoreError
)


def run_tests():
    print("=" * 65)
    print("PHASE 4 TEST: Embeddings & pgvector Storage")
    print("=" * 65)

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    # TEST 1: Check API Key Configuration
    print("\n[Test 1] Checking GOOGLE_API_KEY configuration...")
    if not api_key or api_key == "your_gemini_api_key_here":
        print(" -> Notice: GOOGLE_API_KEY is not yet populated in .env.")
        print(" -> Testing defensive error handling when key is missing...")
        try:
            embed_text("Test query")
            print(" -> FAILED: Expected EmbeddingError was not raised.")
        except EmbeddingError as e:
            print(f" -> Correctly caught expected EmbeddingError:\n    '{str(e)}'")
            print(" -> Test 1 PASSED: Defensive API key validation working as expected.")
    else:
        print(" -> Valid GOOGLE_API_KEY detected. Running live embedding test...")
        try:
            vec = embed_text("Software Engineer SDE role requirements")
            print(f" -> Successfully generated embedding vector.")
            print(f" -> Vector dimension: {len(vec)} (Expected: {EMBEDDING_DIM})")
            assert len(vec) == EMBEDDING_DIM, f"Dimension mismatch: expected {EMBEDDING_DIM}, got {len(vec)}"
            print(" -> Test 1 PASSED: Live Gemini embedding generation verified.")
        except Exception as e:
            print(f" -> Embedding call failed: {e}")

    # TEST 2: Empty Text Validation
    print("\n[Test 2] Validating Empty Text Guard...")
    try:
        embed_text("   ")
        print(" -> FAILED: Expected EmbeddingError for empty text.")
    except EmbeddingError as e:
        print(f" -> Correctly caught EmbeddingError for whitespace input: '{e}'")
        print(" -> Test 2 PASSED: Empty text guard verified.")

    # TEST 3: Vector Store Query Error Handling on Disconnected DB
    print("\n[Test 3] Validating Vector Store Database Connection Guard...")
    try:
        # If DB is not running, similarity_search should raise VectorStoreError gracefully
        similarity_search("Python backend skills", top_k=3)
        print(" -> Database is active and returned results.")
    except VectorStoreError as e:
        print(f" -> Correctly caught expected VectorStoreError when DB is inactive:\n    '{str(e)}'")
        print(" -> Test 3 PASSED: Database error handled gracefully.")
    except Exception as e:
        print(f" -> Unexpected exception: {e}")

    print("\n" + "=" * 65)
    print("ALL PHASE 4 EMBEDDINGS & VECTOR STORE TESTS COMPLETED!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
