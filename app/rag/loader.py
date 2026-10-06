"""
PDF Loader module for AI Placement Intelligence Platform:
Extracts text and page-level metadata from Job Description (JD) PDF files.
Handles empty, corrupted, and multi-page documents gracefully.
"""

import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class PDFLoadError(Exception):
    """Custom exception raised when PDF loading fails."""
    pass


def load_pdf(file_path: str) -> List[Document]:
    """
    Loads and extracts pages from a Job Description PDF.

    Args:
        file_path (str): Absolute or relative path to the PDF file.

    Returns:
        List[Document]: List of LangChain Document objects with page content and metadata.

    Raises:
        PDFLoadError: If file is missing, empty, corrupted, or has no extractable text.
    """
    # 1. Check file existence
    if not os.path.exists(file_path):
        raise PDFLoadError(f"File not found: '{file_path}'")

    # 2. Check file extension
    if not file_path.lower().endswith(".pdf"):
        raise PDFLoadError(f"Invalid file format: '{file_path}'. Only .pdf files are supported.")

    # 3. Check for empty file (0 bytes)
    if os.path.getsize(file_path) == 0:
        raise PDFLoadError(f"Uploaded file is empty (0 bytes): '{os.path.basename(file_path)}'")

    try:
        # 4. Load pages using PyPDFLoader
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        if not pages:
            raise PDFLoadError(f"PDF contains no pages: '{os.path.basename(file_path)}'")

        # 5. Check if document has any extractable text (e.g. Scanned image PDFs)
        total_text_length = sum(len(page.page_content.strip()) for page in pages)
        if total_text_length == 0:
            raise PDFLoadError(
                f"PDF contains no extractable text: '{os.path.basename(file_path)}'. "
                "The file may be a scanned image or protected."
            )

        # Standardize page numbers to 1-indexed (pypdf is 0-indexed by default)
        filename = os.path.basename(file_path)
        for page in pages:
            raw_page = page.metadata.get("page", 0)
            page.metadata["page_number"] = raw_page + 1
            page.metadata["source_filename"] = filename

        return pages

    except PDFLoadError:
        raise
    except Exception as e:
        raise PDFLoadError(f"Failed to read PDF '{os.path.basename(file_path)}': {str(e)}")
