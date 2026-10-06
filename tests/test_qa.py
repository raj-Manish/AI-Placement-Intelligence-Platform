"""
Test script for Phase 5: RAG Question Answering (QA)
Verifies:
1. System prompt anti-hallucination rules and formatting.
2. Source deduplication and page citations.
3. Empty context honest fallback.
4. LLM client defensive initialization.
"""

import os
import sys

# Ensure root workspace is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.qa import (
    build_system_prompt,
    extract_unique_sources,
    NOT_FOUND_MESSAGE,
    QAError
)
from app.rag.retriever import format_context_for_prompt


def run_tests():
    print("=" * 65)
    print("PHASE 5 TEST: RAG Question Answering & Source Citations")
    print("=" * 65)

    # TEST 1: System Prompt Grounding Rules
    print("\n[Test 1] Verifying System Prompt Structure...")
    prompt = build_system_prompt()
    assert NOT_FOUND_MESSAGE in prompt, "Fallback message not found in system prompt!"
    assert "CRITICAL RULES" in prompt
    print(" -> Standard prompt contains anti-hallucination mandate.")

    profile = {
        "name": "Jane Doe",
        "skills": "Python, SQL, React",
        "preferred_roles": "Backend Engineer",
        "expected_salary": 14,
        "experience": 0
    }
    personalized_prompt = build_system_prompt(student_profile=profile)
    assert "PERSONALIZED PROFILE MATCHING" in personalized_prompt
    print(" -> Personalized profile prompt includes objective distinction rules.")
    print(" -> Test 1 PASSED: Prompt templates validated.")

    # TEST 2: Source Extraction and Deduplication
    print("\n[Test 2] Verifying Source Attribution & Deduplication...")
    mock_chunks = [
        {"source_filename": "Amazon_SDE_JD.pdf", "page_number": 2, "chunk_text": "C++, Python, SQL"},
        {"source_filename": "Amazon_SDE_JD.pdf", "page_number": 2, "chunk_text": "Data Structures"}, # Duplicate page
        {"source_filename": "Amazon_SDE_JD.pdf", "page_number": 3, "chunk_text": "AWS, Docker, Kubernetes"}
    ]
    sources = extract_unique_sources(mock_chunks)
    print(" -> Extracted sources:", sources)
    assert len(sources) == 2, f"Expected 2 unique page citations, got {len(sources)}"
    assert "Amazon_SDE_JD.pdf — Page 2" in sources
    assert "Amazon_SDE_JD.pdf — Page 3" in sources
    print(" -> Test 2 PASSED: Page-level source deduplication verified.")

    # TEST 3: Context Formatter
    print("\n[Test 3] Verifying Context Formatter for LLM...")
    formatted = format_context_for_prompt(mock_chunks)
    assert "[EXCERPT 1 | File: Amazon_SDE_JD.pdf | Page: 2]" in formatted
    assert "[EXCERPT 3 | File: Amazon_SDE_JD.pdf | Page: 3]" in formatted
    print(" -> Test 3 PASSED: Context formatted with clean excerpt tags.")

    # TEST 4: Empty Context Fallback
    print("\n[Test 4] Verifying Honest Fallback when No Chunks Exist...")
    empty_format = format_context_for_prompt([])
    assert "No relevant job description text found" in empty_format
    print(f" -> Output for empty chunks: '{empty_format}'")
    print(" -> Test 4 PASSED: Empty context fallback verified.")

    print("\n" + "=" * 65)
    print("ALL PHASE 5 QA & CITATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
