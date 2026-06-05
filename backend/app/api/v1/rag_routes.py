from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas.rag_schema import IngestRequest, RAGQueryRequest, RAGQueryResponse
from app.services.rag.pipeline import RAGPipelineService
from app.utils.observability import get_logger, log_event

router  = APIRouter(prefix="/api/v1/rag", tags=["rag"])
logger  = get_logger(__name__)

_service: RAGPipelineService | None = None


def _get_service() -> RAGPipelineService:
    global _service
    if _service is None:
        _service = RAGPipelineService()
    return _service


@router.post("/ingest")
async def ingest_documents(request: IngestRequest) -> dict:
    """
    Ingest documents into all 3 vector stores (FAISS, Pinecone, Chroma)
    and store document metadata in MongoDB.
    """
    try:
        result = await _get_service().ingest(request)
        log_event(logger, "rag_ingest_completed",
                  documents=result["documents"],
                  chunks=result["chunks"],
                  mongo_stored=result.get("mongo_stored", 0))
        return result
    except Exception as exc:
        log_event(logger, "rag_ingest_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to ingest documents") from exc


@router.post("/query", response_model=RAGQueryResponse)
async def query_documents(request: RAGQueryRequest) -> RAGQueryResponse:
    """
    Run async RAG pipeline across selected vector backends.
    Results are enriched with MongoDB document metadata where available.
    """
    try:
        response = await _get_service().query(request.query, request.top_k, request.use_providers)
        log_event(logger, "rag_query_completed",
                  top_k=request.top_k,
                  providers=request.use_providers,
                  degraded=response.degraded,
                  total_tokens=response.token_usage.get("total_tokens", 0))
        return response
    except Exception as exc:
        log_event(logger, "rag_query_failed", error=str(exc), query=request.query)
        raise HTTPException(
            status_code=502,
            detail="RAG pipeline failed — retry or reduce top_k.",
        ) from exc


@router.get("/benchmark")
async def benchmark_retrieval(
    query: str = Query(default="content marketing strategy for B2B SaaS"),
    top_k: int = Query(default=5, ge=1, le=20),
) -> dict:
    """
    Benchmark retrieval latency across all 3 vector backends independently.
    Returns per-provider latency, hit count, and sub-200ms pass/fail.
    """
    try:
        return await _get_service().benchmark(query, top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/mongo/status")
async def mongo_status() -> dict:
    """Check MongoDB connection status and document count."""
    return await _get_service()._mongo.health_check()


@router.get("/mongo/documents")
async def list_mongo_documents() -> list[dict]:
    """List all documents stored in MongoDB (metadata only, no vectors)."""
    return await _get_service()._mongo.list_all()
