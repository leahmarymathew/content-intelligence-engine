from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IngestDocument(BaseModel):
    """Single source document to ingest into vector stores."""

    doc_id: str = Field(..., description="Unique source document identifier")
    text: str = Field(..., min_length=1, description="Raw document text")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestRequest(BaseModel):
    """Batch ingestion payload."""

    documents: list[IngestDocument]
    chunk_size: int = Field(default=500, ge=100, le=4000)
    chunk_overlap: int = Field(default=80, ge=0, le=1000)


class RAGQueryRequest(BaseModel):
    """Query payload for RAG generation endpoint."""

    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)
    use_providers: list[str] = Field(default_factory=lambda: ["faiss", "pinecone", "chroma"])


class SourceChunk(BaseModel):
    """Returned evidence item used for generation."""

    provider: str
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGQueryResponse(BaseModel):
    """Validated RAG response."""

    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[SourceChunk]
    token_usage: dict[str, int]
    latency_ms: dict[str, float]
    degraded: bool = False
