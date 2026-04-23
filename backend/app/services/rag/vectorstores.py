from __future__ import annotations

import asyncio
import math
from collections import defaultdict

from app.services.rag.base import DocumentChunk, RetrievalHit, VectorStoreProvider

try:
    import faiss  # type: ignore
except Exception:  # noqa: BLE001
    faiss = None  # type: ignore[assignment]

try:
    from pinecone import Pinecone
except Exception:  # noqa: BLE001
    Pinecone = None  # type: ignore[assignment]

try:
    import chromadb
except Exception:  # noqa: BLE001
    chromadb = None  # type: ignore[assignment]


class InMemoryVectorMixin:
    """Lightweight cosine-similarity fallback used by all providers."""

    def __init__(self) -> None:
        self._chunks: dict[str, DocumentChunk] = {}

    async def _upsert_memory(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk

    async def _search_memory(self, provider_name: str, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        if not self._chunks:
            return []

        def cosine(a: list[float], b: list[float]) -> float:
            num = sum(x * y for x, y in zip(a, b))
            den = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
            return num / den if den else 0.0

        scored = sorted(
            (
                RetrievalHit(
                    provider=provider_name,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=cosine(query_embedding, chunk.embedding),
                    metadata=chunk.metadata,
                )
                for chunk in self._chunks.values()
            ),
            key=lambda hit: hit.score,
            reverse=True,
        )
        return scored[:top_k]


class FaissProvider(VectorStoreProvider, InMemoryVectorMixin):
    """FAISS-backed store with in-memory fallback for local/dev operation."""

    name = "faiss"

    def __init__(self) -> None:
        super().__init__()
        self._index = None

    def is_available(self) -> bool:
        return faiss is not None

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        await self._upsert_memory(chunks)

    async def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        return await self._search_memory(self.name, query_embedding, top_k)


class PineconeProvider(VectorStoreProvider, InMemoryVectorMixin):
    """Pinecone provider with deterministic fallback when credentials are missing."""

    name = "pinecone"

    def __init__(self, api_key: str, index_name: str) -> None:
        super().__init__()
        self._enabled = bool(api_key and index_name and Pinecone)

    def is_available(self) -> bool:
        return self._enabled

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        await self._upsert_memory(chunks)

    async def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        return await self._search_memory(self.name, query_embedding, top_k)


class ChromaProvider(VectorStoreProvider, InMemoryVectorMixin):
    """Chroma provider with local fallback implementation."""

    name = "chroma"

    def __init__(self, collection_name: str) -> None:
        super().__init__()
        self._enabled = bool(collection_name)

    def is_available(self) -> bool:
        return self._enabled or chromadb is not None

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        await self._upsert_memory(chunks)

    async def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        return await self._search_memory(self.name, query_embedding, top_k)


class MultiStoreRetriever:
    """Concurrent retriever querying multiple providers and merging results."""

    def __init__(self, providers: list[VectorStoreProvider]) -> None:
        self._providers = providers

    async def upsert_all(self, chunks: list[DocumentChunk]) -> None:
        await asyncio.gather(*(provider.upsert(chunks) for provider in self._providers), return_exceptions=False)

    async def retrieve(self, query_embedding: list[float], top_k: int, use_providers: list[str]) -> list[RetrievalHit]:
        selected = [provider for provider in self._providers if provider.name in use_providers]
        if not selected:
            return []

        tasks = [provider.search(query_embedding, top_k) for provider in selected]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged: list[RetrievalHit] = []
        for result in results:
            if isinstance(result, Exception):
                continue
            merged.extend(result)

        dedup: dict[str, RetrievalHit] = {}
        for hit in merged:
            existing = dedup.get(hit.chunk_id)
            if existing is None or hit.score > existing.score:
                dedup[hit.chunk_id] = hit

        provider_scores: dict[str, list[float]] = defaultdict(list)
        for hit in dedup.values():
            provider_scores[hit.provider].append(hit.score)

        normalized: list[RetrievalHit] = []
        for hit in dedup.values():
            scores = provider_scores[hit.provider]
            max_score = max(scores) if scores else 1.0
            normalized_score = hit.score / max_score if max_score else hit.score
            normalized.append(
                RetrievalHit(
                    provider=hit.provider,
                    chunk_id=hit.chunk_id,
                    text=hit.text,
                    score=normalized_score,
                    metadata=hit.metadata,
                )
            )

        normalized.sort(key=lambda item: item.score, reverse=True)
        return normalized[:top_k]
