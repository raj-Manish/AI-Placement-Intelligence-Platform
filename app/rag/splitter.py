"""
Text Splitter module for AI Placement Intelligence Platform:
Splits loaded PDF pages into semantically cohesive chunks using RecursiveCharacterTextSplitter.
Preserves page numbers, source filenames, and assigns sequential chunk indexes.
"""

from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_documents(
    documents: List[Document],
    chunk_size: int = 900,
    chunk_overlap: int = 120
) -> List[Document]:
    """
    Splits a list of page documents into smaller overlapping text chunks.

    Args:
        documents (List[Document]): Raw pages from PDF loader.
        chunk_size (int): Maximum character length per chunk (default: 900).
        chunk_overlap (int): Overlap between successive chunks to preserve context (default: 120).

    Returns:
        List[Document]: Chunks with preserved page numbers and unique chunk indices.
    """
    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )

    split_chunks: List[Document] = []
    chunk_counter = 0

    for doc in documents:
        # Split text from the single page
        sub_chunks = splitter.split_text(doc.page_content)
        page_num = doc.metadata.get("page_number", 1)
        source_name = doc.metadata.get("source_filename", "unknown.pdf")

        for text in sub_chunks:
            cleaned_text = text.strip()
            if not cleaned_text:
                continue

            metadata: Dict[str, Any] = {
                "chunk_index": chunk_counter,
                "page_number": page_num,
                "source_filename": source_name,
                "char_length": len(cleaned_text)
            }

            split_chunks.append(Document(page_content=cleaned_text, metadata=metadata))
            chunk_counter += 1

    return split_chunks


def debug_print_chunks(chunks: List[Document], max_display: int = 3) -> None:
    """Utility to print chunks in terminal for debugging and inspection."""
    print(f"\n--- Ingestion Debug: Total Chunks Created = {len(chunks)} ---")
    for i, chunk in enumerate(chunks[:max_display]):
        print(f"\n[Chunk {chunk.metadata.get('chunk_index')}]")
        print(f"Source: {chunk.metadata.get('source_filename')} | Page: {chunk.metadata.get('page_number')} | Length: {chunk.metadata.get('char_length')} chars")
        print(f"Preview:\n{chunk.page_content[:200]}...")
        print("-" * 50)
    if len(chunks) > max_display:
        print(f"... and {len(chunks) - max_display} more chunks.")
