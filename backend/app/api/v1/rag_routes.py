from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.rag_schema import IngestRequest, RAGQueryRequest, RAGQueryResponse
from app.services.rag.pipeline import RAGPipelineService
from app.utils.observability import get_logger, log_event

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])
logger = get_logger(__name__)
service = RAGPipelineService()


@router.post("/ingest")
async def ingest_documents(request: IngestRequest) -> dict[str, int]:
    """Ingest documents into all configured vector stores."""

    try:
        result = await service.ingest(request)
        log_event(logger, "rag_ingest_completed", documents=result["documents"], chunks=result["chunks"])
        return result
    except Exception as exc:  # noqa: BLE001
        log_event(logger, "rag_ingest_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to ingest documents") from exc


@router.post("/query", response_model=RAGQueryResponse)
async def query_documents(request: RAGQueryRequest) -> RAGQueryResponse:
    """Run async RAG pipeline with retrieval, generation and validation."""

    try:
        response = await service.query(request.query, request.top_k, request.use_providers)
        log_event(
            logger,
            "rag_query_completed",
            top_k=request.top_k,
            degraded=response.degraded,
            total_tokens=response.token_usage.get("total_tokens", 0),
        )
        return response
    except Exception as exc:  # noqa: BLE001
        log_event(logger, "rag_query_failed", error=str(exc), query=request.query)
        raise HTTPException(
            status_code=502,
            detail="RAG pipeline failed. Please retry or reduce top_k for degraded fallback.",
        ) from exc
