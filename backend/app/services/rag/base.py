from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    """Immutable chunk stored in vector indexes."""

    chunk_id: str
    doc_id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    """Normalized retrieval result independent of provider SDK."""

    provider: str
    chunk_id: str
    text: str
    score: float
    metadata: dict[str, Any]


class VectorStoreProvider(ABC):
    """Abstract contract for pluggable vector stores."""

    name: str

    @abstractmethod
    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        """Insert or update chunks."""

    @abstractmethod
    async def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        """Return top-K nearest chunks for the query vector."""

    @abstractmethod
    def is_available(self) -> bool:
        """Indicate provider runtime availability."""
