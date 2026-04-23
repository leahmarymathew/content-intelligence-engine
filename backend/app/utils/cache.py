from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class CacheEntry(Generic[T]):
    """Single TTL cache entry."""

    value: T
    expires_at: float


class AsyncTTLCache(Generic[T]):
    """Simple async-safe in-memory TTL cache for low-latency lookups."""

    def __init__(self, ttl_seconds: int = 300, max_items: int = 1000) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_items = max_items
        self._store: dict[str, CacheEntry[T]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> T | None:
        """Return cached value if key exists and is not expired."""

        async with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            if item.expires_at < time.time():
                self._store.pop(key, None)
                return None
            return item.value

    async def set(self, key: str, value: T) -> None:
        """Write cache entry and evict oldest entries when at capacity."""

        async with self._lock:
            if len(self._store) >= self._max_items:
                oldest_key = min(self._store, key=lambda k: self._store[k].expires_at)
                self._store.pop(oldest_key, None)
            self._store[key] = CacheEntry(value=value, expires_at=time.time() + self._ttl_seconds)
