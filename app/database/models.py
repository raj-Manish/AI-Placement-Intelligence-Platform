"""
SQLAlchemy ORM Models for AI Placement Intelligence Platform:
1. Document: Metadata for uploaded JD PDFs.
2. DocumentChunk: Text chunks with page numbers and 768-dim embeddings.
3. Company: Benchmark hiring dataset for the deterministic matching engine.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.database.connection import Base


class Document(Base):
    """Stores metadata for uploaded job description documents."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False, index=True)
    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationship: 1 Document -> Many Chunks
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Document(id={self.id}, company='{self.company_name}', filename='{self.filename}')>"


class DocumentChunk(Base):
    """
    Stores individual text chunks from a JD along with the exact page number
    and high-dimensional vector embedding for pgvector cosine similarity search.
    """
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    # Gemini text-embedding-004 produces 768-dimensional vectors
    embedding = Column(Vector(768), nullable=True)

    # Back-reference to parent document
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, page={self.page_number})>"


class Company(Base):
    """
    Benchmark target companies used by the deterministic rule-based matching engine.
    Contains skill requirements, salary brackets, and historical hiring notes.
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, index=True)
    role = Column(String(255), nullable=False, index=True)
    required_skills = Column(Text, nullable=False)  # Comma-separated list of skills
    min_salary = Column(Float, nullable=False)      # In LPA (Lakhs Per Annum)
    max_salary = Column(Float, nullable=False)      # In LPA
    hiring_history = Column(String(255), nullable=False)  # E.g. "Regular Tier-1 SDE Hiring"

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.company_name}', role='{self.role}')>"
