from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

from app.utils.cache import AsyncTTLCache

try:
    from langchain_openai import OpenAIEmbeddings
except Exception:  # noqa: BLE001
    OpenAIEmbeddings = None  # type: ignore[assignment]


class EmbeddingService(ABC):
    """Embedding contract for RAG components."""

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """Embed user query text."""

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed batch of document chunks."""


class LangChainEmbeddingService(EmbeddingService):
    """LangChain embedding wrapper with cache and deterministic fallback."""

    def __init__(self, openai_api_key: str) -> None:
        self._cache: AsyncTTLCache[list[float]] = AsyncTTLCache(ttl_seconds=1200, max_items=10000)
        self._batch_cache: AsyncTTLCache[list[list[float]]] = AsyncTTLCache(ttl_seconds=1200, max_items=1000)
        self._model = OpenAIEmbeddings(api_key=openai_api_key) if openai_api_key and OpenAIEmbeddings else None

    async def embed_query(self, query: str) -> list[float]:
        cached = await self._cache.get(query)
        if cached is not None:
            return cached

        if self._model is not None:
            vector = await self._model.aembed_query(query)
        else:
            vector = self._pseudo_embedding(query)

        await self._cache.set(query, vector)
        return vector

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        cache_key = "|".join(texts)
        cached = await self._batch_cache.get(cache_key)
        if cached is not None:
            return cached

        if self._model is not None:
            vectors = await self._model.aembed_documents(texts)
        else:
            vectors = [self._pseudo_embedding(text) for text in texts]

        await self._batch_cache.set(cache_key, vectors)
        return vectors

    @staticmethod
    def _pseudo_embedding(text: str, dims: int = 32) -> list[float]:
        """Offline-safe deterministic embedding used when API credentials are absent."""

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [((digest[i % len(digest)] / 255.0) * 2.0) - 1.0 for i in range(dims)]
