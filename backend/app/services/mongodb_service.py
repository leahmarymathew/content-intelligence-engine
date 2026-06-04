"""
MongoDB document metadata store.

Stores structured metadata for every document ingested into the RAG pipeline.
Sits alongside the vector indices — vectors go to FAISS/Pinecone/Chroma,
metadata (title, source, content_type, word_count, etc.) goes here.

Degrades gracefully: if MONGODB_URL is not set the store is a no-op and
the rest of the pipeline continues working.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    AsyncIOMotorClient = None  # type: ignore[assignment]


class MongoDocumentStore:
    """Async MongoDB store for RAG document metadata."""

    def __init__(self, url: str = "") -> None:
        self._enabled = False
        self._client = None
        self._collection = None

        if not url or not AsyncIOMotorClient:
            return

        try:
            self._client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=3000)
            db = self._client["content_intelligence"]
            self._collection = db["documents"]
            self._enabled = True
            logger.info("MongoDB document store connected.")
        except Exception as exc:
            logger.warning("MongoDB unavailable — metadata will not be persisted: %s", exc)

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def store(self, doc_id: str, text_preview: str, metadata: dict) -> None:
        """Upsert document metadata. Silently skipped when store is disabled."""
        if not self._enabled:
            return
        try:
            await self._collection.update_one(
                {"doc_id": doc_id},
                {
                    "$set": {
                        "doc_id":       doc_id,
                        "text_preview": text_preview[:500],
                        "metadata":     metadata,
                        "indexed_at":   datetime.now(tz=timezone.utc),
                    }
                },
                upsert=True,
            )
        except Exception as exc:
            logger.warning("MongoDB store failed for doc %s: %s", doc_id, exc)

    async def get(self, doc_id: str) -> dict | None:
        if not self._enabled:
            return None
        try:
            doc = await self._collection.find_one({"doc_id": doc_id}, {"_id": 0})
            return doc
        except Exception:
            return None

    async def list_all(self) -> list[dict]:
        if not self._enabled:
            return []
        try:
            return await self._collection.find({}, {"_id": 0}).sort("indexed_at", -1).to_list(500)
        except Exception:
            return []

    async def health_check(self) -> dict:
        if not self._enabled:
            return {"status": "disabled", "reason": "MONGODB_URL not configured"}
        try:
            await self._client.admin.command("ping")
            count = await self._collection.count_documents({})
            return {"status": "ok", "documents": count}
        except Exception as exc:
            return {"status": "error", "reason": str(exc)}
