from __future__ import annotations

import pytest

from app.schemas.rag_schema import IngestDocument, IngestRequest
from app.services.rag.pipeline import RAGPipelineService


@pytest.mark.asyncio
async def test_pipeline_ingest_and_query() -> None:
    service = RAGPipelineService()

    ingest_result = await service.ingest(
        IngestRequest(
            documents=[
                IngestDocument(
                    doc_id="doc-1",
                    text="LangChain Expression Language composes prompts, models, and parsers.",
                    metadata={"source": "unit-test"},
                )
            ],
            chunk_size=120,
            chunk_overlap=20,
        )
    )

    assert ingest_result["documents"] == 1
    assert ingest_result["chunks"] >= 1

    response = await service.query("How does LCEL help in production?", top_k=3, providers=["faiss", "chroma", "pinecone"])

    assert response.answer
    assert response.token_usage["total_tokens"] >= 0
    assert "total" in response.latency_ms
