from __future__ import annotations

import asyncio
import math
from collections import defaultdict

from app.services.rag.base import DocumentChunk, RetrievalHit, VectorStoreProvider

try:
    import numpy as np
except Exception:  # noqa: BLE001
    np = None  # type: ignore[assignment]

try:
    import faiss  # type: ignore
except Exception:  # noqa: BLE001
    faiss = None  # type: ignore[assignment]

try:
    from pinecone import Pinecone as PineconeClient
except Exception:  # noqa: BLE001
    PineconeClient = None  # type: ignore[assignment]

try:
    import chromadb
except Exception:  # noqa: BLE001
    chromadb = None  # type: ignore[assignment]


# ─── In-memory cosine fallback (used when a backend isn't configured) ─────────

class InMemoryVectorMixin:
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
            key=lambda h: h.score,
            reverse=True,
        )
        return scored[:top_k]


# ─── FAISS ────────────────────────────────────────────────────────────────────

class FaissProvider(VectorStoreProvider, InMemoryVectorMixin):
    """FAISS IndexIDMap with cosine similarity. Falls back to in-memory when faiss/numpy unavailable."""

    name = "faiss"

    def __init__(self) -> None:
        super().__init__()
        self._index = None                        # faiss.IndexIDMap wrapping IndexFlatIP
        self._id_to_int: dict[str, int] = {}      # chunk_id  -> faiss int id
        self._int_to_chunk: dict[int, DocumentChunk] = {}
        self._next_id: int = 0

    def is_available(self) -> bool:
        return faiss is not None and np is not None

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        await self._upsert_memory(chunks)
        if not self.is_available() or not chunks:
            return

        dim = len(chunks[0].embedding)
        if self._index is None:
            self._index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))

        vecs, ids = [], []
        for chunk in chunks:
            if chunk.chunk_id not in self._id_to_int:
                self._id_to_int[chunk.chunk_id] = self._next_id
                self._next_id += 1
            int_id = self._id_to_int[chunk.chunk_id]
            self._int_to_chunk[int_id] = chunk

            v = np.array(chunk.embedding, dtype="float32")
            norm = np.linalg.norm(v)
            vecs.append(v / norm if norm > 0 else v)
            ids.append(int_id)

        self._index.add_with_ids(
            np.array(vecs, dtype="float32"),
            np.array(ids, dtype="int64"),
        )

    async def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        if not self.is_available() or self._index is None or self._index.ntotal == 0:
            return await self._search_memory(self.name, query_embedding, top_k)

        q = np.array([query_embedding], dtype="float32")
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm

        k = min(top_k, self._index.ntotal)
        scores, int_ids = self._index.search(q, k)

        hits = []
        for score, int_id in zip(scores[0], int_ids[0]):
            if int_id < 0:
                continue
            chunk = self._int_to_chunk.get(int_id)
            if chunk:
                hits.append(RetrievalHit(
                    provider=self.name,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=float(score),
                    metadata=chunk.metadata,
                ))
        return hits


# ─── Pinecone ─────────────────────────────────────────────────────────────────

class PineconeProvider(VectorStoreProvider, InMemoryVectorMixin):
    """Pinecone provider — uses real index when API key + index exist, in-memory otherwise."""

    name = "pinecone"

    def __init__(self, api_key: str, index_name: str) -> None:
        super().__init__()
        self._real_index = None
        self._index_name = index_name

        if api_key and index_name and PineconeClient:
            try:
                pc = PineconeClient(api_key=api_key)
                existing = [idx.name for idx in pc.list_indexes()]
                if index_name in existing:
                    self._real_index = pc.Index(index_name)
            except Exception:
                pass

    def is_available(self) -> bool:
        return True  # always available, degrades to in-memory

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        await self._upsert_memory(chunks)
        if not self._real_index or not chunks:
            return

        vectors = [
            {
                "id": chunk.chunk_id,
                "values": chunk.embedding,
                "metadata": {**(chunk.metadata or {}), "_text": chunk.text[:1000]},
            }
            for chunk in chunks
        ]
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, lambda: self._real_index.upsert(vectors=vectors))
        except Exception:
            pass

    async def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        if not self._real_index:
            return await self._search_memory(self.name, query_embedding, top_k)

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self._real_index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True,
                ),
            )
            hits = []
            for match in result.matches:
                meta = dict(match.metadata) if match.metadata else {}
                text = meta.pop("_text", "")
                hits.append(RetrievalHit(
                    provider=self.name,
                    chunk_id=match.id,
                    text=text,
                    score=float(match.score),
                    metadata=meta,
                ))
            return hits
        except Exception:
            return await self._search_memory(self.name, query_embedding, top_k)


# ─── Chroma ───────────────────────────────────────────────────────────────────

class ChromaProvider(VectorStoreProvider, InMemoryVectorMixin):
    """Chroma provider — uses real local DB when chromadb is available, in-memory otherwise."""

    name = "chroma"

    def __init__(self, collection_name: str) -> None:
        super().__init__()
        self._collection = None

        if collection_name and chromadb:
            try:
                client = chromadb.Client()
                self._collection = client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception:
                pass

    def is_available(self) -> bool:
        return True

    async def upsert(self, chunks: list[DocumentChunk]) -> None:
        await self._upsert_memory(chunks)
        if not self._collection or not chunks:
            return

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self._collection.upsert(
                    ids=[c.chunk_id for c in chunks],
                    embeddings=[c.embedding for c in chunks],
                    documents=[c.text for c in chunks],
                    metadatas=[c.metadata or {} for c in chunks],
                ),
            )
        except Exception:
            pass

    async def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        if not self._collection:
            return await self._search_memory(self.name, query_embedding, top_k)

        loop = asyncio.get_event_loop()
        try:
            count = await loop.run_in_executor(None, self._collection.count)
            if count == 0:
                return []

            results = await loop.run_in_executor(
                None,
                lambda: self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k, count),
                    include=["documents", "metadatas", "distances"],
                ),
            )
            hits = []
            for chunk_id, doc, meta, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                hits.append(RetrievalHit(
                    provider=self.name,
                    chunk_id=chunk_id,
                    text=doc,
                    score=1.0 - float(distance),  # cosine distance → similarity
                    metadata=meta or {},
                ))
            return hits
        except Exception:
            return await self._search_memory(self.name, query_embedding, top_k)


# ─── Multi-store retriever ────────────────────────────────────────────────────

class MultiStoreRetriever:
    """Concurrent retriever that queries multiple providers and merges results."""

    def __init__(self, providers: list[VectorStoreProvider]) -> None:
        self._providers = providers

    async def upsert_all(self, chunks: list[DocumentChunk]) -> None:
        await asyncio.gather(*(p.upsert(chunks) for p in self._providers), return_exceptions=False)

    async def retrieve(self, query_embedding: list[float], top_k: int, use_providers: list[str]) -> list[RetrievalHit]:
        selected = [p for p in self._providers if p.name in use_providers]
        if not selected:
            return []

        results = await asyncio.gather(*[p.search(query_embedding, top_k) for p in selected], return_exceptions=True)

        merged: list[RetrievalHit] = []
        for result in results:
            if not isinstance(result, Exception):
                merged.extend(result)

        # Deduplicate by chunk_id keeping highest score
        dedup: dict[str, RetrievalHit] = {}
        for hit in merged:
            if hit.chunk_id not in dedup or hit.score > dedup[hit.chunk_id].score:
                dedup[hit.chunk_id] = hit

        # Normalise scores within each provider
        provider_scores: dict[str, list[float]] = defaultdict(list)
        for hit in dedup.values():
            provider_scores[hit.provider].append(hit.score)

        normalised = []
        for hit in dedup.values():
            scores = provider_scores[hit.provider]
            max_s = max(scores) if scores else 1.0
            normalised.append(RetrievalHit(
                provider=hit.provider,
                chunk_id=hit.chunk_id,
                text=hit.text,
                score=hit.score / max_s if max_s else hit.score,
                metadata=hit.metadata,
            ))

        normalised.sort(key=lambda h: h.score, reverse=True)
        return normalised[:top_k]
