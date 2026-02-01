"""SQLAlchemy ORM models for the resurch database."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Paper(Base):
    """Academic paper metadata."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doi = Column(String(255), unique=True, nullable=True, index=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    year = Column(Integer, nullable=True, index=True)
    publication = Column(String(500), nullable=True)
    publisher = Column(String(500), nullable=True)
    citations = Column(Integer, default=0, index=True)
    doi_url = Column(String(500), nullable=True)
    publisher_url = Column(String(1000), nullable=True)
    pdf_url = Column(String(1000), nullable=True)
    authors = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sources = relationship("PaperSource", back_populates="paper", cascade="all, delete-orphan")
    enrichments = relationship("Enrichment", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Paper(id={self.id}, title='{self.title[:50]}...', doi='{self.doi}')>"


class PaperSource(Base):
    """Track which repository found each paper."""

    __tablename__ = "paper_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    repository = Column(String(100), nullable=False, index=True)
    external_id = Column(String(500), nullable=True)
    raw_data = Column(Text, nullable=True)  # JSON
    retrieved_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraint on paper_id + repository
    __table_args__ = (UniqueConstraint("paper_id", "repository", name="uix_paper_repository"),)

    # Relationships
    paper = relationship("Paper", back_populates="sources")

    def __repr__(self) -> str:
        return f"<PaperSource(paper_id={self.paper_id}, repository='{self.repository}')>"


class Search(Base):
    """Resumable search tracking."""

    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    repository = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)  # pending/in_progress/completed/interrupted
    total_results = Column(Integer, nullable=True)
    fetched_results = Column(Integer, default=0)
    last_page = Column(Integer, default=0)
    cursor = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Search(id={self.id}, query='{self.query[:30]}...', status='{self.status}')>"


class Enrichment(Base):
    """Resumable enrichment tracking."""

    __tablename__ = "enrichments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    enrichment_type = Column(String(50), nullable=False)  # abstract/doi/citations/pdf
    status = Column(String(50), default="pending", index=True)  # pending/completed/failed
    source = Column(String(100), nullable=True)
    attempted_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Unique constraint on paper_id + enrichment_type
    __table_args__ = (UniqueConstraint("paper_id", "enrichment_type", name="uix_paper_enrichment"),)

    # Relationships
    paper = relationship("Paper", back_populates="enrichments")

    def __repr__(self) -> str:
        return f"<Enrichment(paper_id={self.paper_id}, type='{self.enrichment_type}', status='{self.status}')>"
