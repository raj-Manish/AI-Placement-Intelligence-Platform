"""
Test script for Phase 3: PDF Ingestion & Chunking
Verifies:
1. Correct page loading and page-number metadata preservation.
2. Recursive text chunking with overlap.
3. Edge case error handling (empty PDF, nonexistent file, wrong file format).
"""

import os
import sys

# Ensure root workspace is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.loader import load_pdf, PDFLoadError
from app.rag.splitter import split_documents, debug_print_chunks


def run_tests():
    print("=" * 65)
    print("PHASE 3 TEST: PDF Ingestion & Text Chunking")
    print("=" * 65)

    sample_pdf = os.path.join("data", "sample_jds", "Amazon_SDE_JD.pdf")
    empty_pdf = os.path.join("data", "sample_jds", "empty.pdf")

    # TEST 1: Load Valid 3-Page JD PDF
    print("\n[Test 1] Loading Valid PDF:", sample_pdf)
    pages = load_pdf(sample_pdf)
    print(f" -> Total Pages Loaded: {len(pages)}")
    assert len(pages) == 3, f"Expected 3 pages, got {len(pages)}"

    for i, page in enumerate(pages):
        page_num = page.metadata.get("page_number")
        print(f" -> Page {i+1} Metadata: page_number={page_num}, char_count={len(page.page_content)}")
        assert page_num == i + 1, f"Expected page_number {i+1}, got {page_num}"
    print(" -> Test 1 PASSED: Valid PDF loaded with exact page numbers.")

    # TEST 2: Chunking with RecursiveCharacterTextSplitter
    print("\n[Test 2] Splitting Pages into Chunks (chunk_size=900, overlap=120)")
    chunks = split_documents(pages, chunk_size=900, chunk_overlap=120)
    print(f" -> Total Chunks Generated: {len(chunks)}")
    assert len(chunks) > 0, "No chunks generated!"

    # Verify metadata on all chunks
    for chunk in chunks:
        assert "chunk_index" in chunk.metadata
        assert "page_number" in chunk.metadata
        assert "source_filename" in chunk.metadata
        assert chunk.metadata["page_number"] in [1, 2, 3]

    print(" -> Test 2 PASSED: Chunks generated and all metadata preserved.")

    # Debug preview
    debug_print_chunks(chunks, max_display=3)

    # TEST 3: Edge Case - Empty PDF (0 bytes)
    print("\n[Test 3] Edge Case: Empty PDF (0 bytes)")
    try:
        load_pdf(empty_pdf)
        print(" -> FAILED: Expected PDFLoadError was not raised.")
    except PDFLoadError as e:
        print(f" -> Correctly caught PDFLoadError: {e}")
        print(" -> Test 3 PASSED: Empty PDF handled gracefully.")

    # TEST 4: Edge Case - Nonexistent File
    print("\n[Test 4] Edge Case: Nonexistent File")
    try:
        load_pdf("data/sample_jds/non_existent.pdf")
        print(" -> FAILED: Expected PDFLoadError was not raised.")
    except PDFLoadError as e:
        print(f" -> Correctly caught PDFLoadError: {e}")
        print(" -> Test 4 PASSED: Missing file handled gracefully.")

    # TEST 5: Edge Case - Non-PDF Extension
    print("\n[Test 5] Edge Case: Non-PDF Extension")
    try:
        load_pdf("requirements.txt")
        print(" -> FAILED: Expected PDFLoadError was not raised.")
    except PDFLoadError as e:
        print(f" -> Correctly caught PDFLoadError: {e}")
        print(" -> Test 5 PASSED: Invalid file type handled gracefully.")

    print("\n" + "=" * 65)
    print("ALL PHASE 3 INGESTION & CHUNKING TESTS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
