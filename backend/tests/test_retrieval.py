from __future__ import annotations

import pytest

from app.services.rag.base import DocumentChunk
from app.services.rag.vectorstores import ChromaProvider, FaissProvider, MultiStoreRetriever, PineconeProvider


@pytest.mark.asyncio
async def test_retrieve_returns_ranked_hits() -> None:
    providers = [
        FaissProvider(),
        PineconeProvider(api_key="", index_name=""),
        ChromaProvider(collection_name="tests"),
    ]
    retriever = MultiStoreRetriever(providers)

    chunks = [
        DocumentChunk(
            chunk_id="doc-1:0",
            doc_id="doc-1",
            text="FastAPI supports async endpoints for high-throughput APIs.",
            embedding=[0.9, 0.1, 0.0],
            metadata={"topic": "async"},
        ),
        DocumentChunk(
            chunk_id="doc-2:0",
            doc_id="doc-2",
            text="RAG systems use vector similarity over embedding spaces.",
            embedding=[0.2, 0.9, 0.1],
            metadata={"topic": "rag"},
        ),
    ]

    await retriever.upsert_all(chunks)
    hits = await retriever.retrieve(query_embedding=[1.0, 0.1, 0.0], top_k=2, use_providers=["faiss", "chroma", "pinecone"])

    assert hits
    assert hits[0].chunk_id == "doc-1:0"
    assert all(hit.score <= 1.0 for hit in hits)
