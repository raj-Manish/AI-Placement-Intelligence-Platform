"""
Vector Store module for AI Placement Intelligence Platform:
Manages storing document chunks with high-dimensional embeddings in PostgreSQL (pgvector)
and executing cosine similarity searches (<=> operator).
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document as LCDocument
from sqlalchemy.orm import Session

from app.database.connection import get_session_factory
from app.database.models import Document, DocumentChunk
from app.rag.embeddings import embed_documents, embed_text


class VectorStoreError(Exception):
    """Custom exception raised for vector store operations."""
    pass


def store_document_chunks(
    filename: str,
    company_name: str,
    chunks: List[LCDocument]
) -> int:
    """
    Embeds and stores document chunks in PostgreSQL using pgvector.
    Replaces existing records with the same filename atomically.

    Args:
        filename (str): Name of the uploaded file.
        company_name (str): Associated company name (e.g. "Amazon").
        chunks (List[LCDocument]): List of text chunks with metadata.

    Returns:
        int: ID of the inserted Document record.
    """
    if not chunks:
        raise VectorStoreError("Cannot store an empty list of chunks.")

    # 1. Generate embeddings for all chunk texts in batch
    chunk_texts = [c.page_content for c in chunks]
    try:
        embeddings = embed_documents(chunk_texts)
    except Exception as e:
        raise VectorStoreError(f"Embedding generation failed during ingestion: {str(e)}")

    if len(embeddings) != len(chunks):
        raise VectorStoreError(
            f"Embedding count mismatch: expected {len(chunks)}, got {len(embeddings)}"
        )

    # 2. Store in PostgreSQL inside an atomic transaction
    SessionFactory = get_session_factory()
    with SessionFactory() as session:
        try:
            # Remove any existing document with the same filename to avoid duplicates
            existing_doc = session.query(Document).filter(Document.filename == filename).first()
            if existing_doc:
                session.delete(existing_doc)
                session.flush()

            # Insert new Document header
            new_doc = Document(
                filename=filename,
                company_name=company_name
            )
            session.add(new_doc)
            session.flush()  # Generates new_doc.id

            # Insert DocumentChunks with 768-dim embeddings
            chunk_models = []
            for i, chunk in enumerate(chunks):
                chunk_obj = DocumentChunk(
                    document_id=new_doc.id,
                    chunk_text=chunk.page_content,
                    page_number=chunk.metadata.get("page_number", 1),
                    chunk_index=chunk.metadata.get("chunk_index", i),
                    embedding=embeddings[i]
                )
                chunk_models.append(chunk_obj)

            session.bulk_save_objects(chunk_models)
            session.commit()
            return new_doc.id

        except Exception as e:
            session.rollback()
            raise VectorStoreError(f"Failed to store chunks in database: {str(e)}")


def similarity_search(
    query: str,
    top_k: int = 4,
    company_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Performs cosine similarity search using pgvector's <=> distance operator.

    Args:
        query (str): User question or search query.
        top_k (int): Number of most relevant chunks to retrieve.
        company_name (Optional[str]): Optional company filter.

    Returns:
        List[Dict[str, Any]]: Top-k relevant chunks with text, page citations, and scores.
    """
    if not query or not query.strip():
        return []

    # 1. Embed query
    try:
        query_vector = embed_text(query.strip())
    except Exception as e:
        raise VectorStoreError(f"Failed to generate query embedding: {str(e)}")

    # 2. Query pgvector using cosine distance
    SessionFactory = get_session_factory()
    with SessionFactory() as session:
        try:
            # DocumentChunk.embedding.cosine_distance(query_vector) maps to <=>
            distance_expr = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")

            query_builder = (
                session.query(DocumentChunk, Document, distance_expr)
                .join(Document, DocumentChunk.document_id == Document.id)
            )

            if company_name:
                query_builder = query_builder.filter(Document.company_name.ilike(f"%{company_name}%"))

            results = (
                query_builder
                .order_by(distance_expr.asc())
                .limit(top_k)
                .all()
            )

            output = []
            for chunk, doc, distance in results:
                # Cosine similarity = 1 - Cosine distance
                cos_dist = float(distance) if distance is not None else 1.0
                similarity_score = round(max(0.0, 1.0 - cos_dist), 4)

                output.append({
                    "chunk_id": chunk.id,
                    "chunk_text": chunk.chunk_text,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "source_filename": doc.filename,
                    "company_name": doc.company_name,
                    "distance": round(cos_dist, 4),
                    "similarity_score": similarity_score
                })

            return output

        except Exception as e:
            raise VectorStoreError(f"Database vector similarity search failed: {str(e)}")


def get_all_documents() -> List[Dict[str, Any]]:
    """Retrieves all uploaded documents with chunk counts for UI status display."""
    SessionFactory = get_session_factory()
    with SessionFactory() as session:
        try:
            docs = session.query(Document).order_by(Document.uploaded_at.desc()).all()
            result = []
            for d in docs:
                chunk_count = session.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
                result.append({
                    "id": d.id,
                    "filename": d.filename,
                    "company_name": d.company_name,
                    "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if d.uploaded_at else "N/A",
                    "chunk_count": chunk_count
                })
            return result
        except Exception:
            return []
