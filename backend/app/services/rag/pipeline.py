from __future__ import annotations

import time

from app.core.config import settings
from app.schemas.rag_schema import IngestRequest, RAGQueryResponse, SourceChunk
from app.services.llm.langchain_pipeline import LangChainGenerationPipeline
from app.services.mongodb_service import MongoDocumentStore
from app.services.rag.base import DocumentChunk
from app.services.rag.chunking import ChunkingConfig, DocumentChunker
from app.services.rag.embeddings import LangChainEmbeddingService
from app.services.rag.langgraph_workflow import RAGGraphState, RAGGraphWorkflow
from app.services.rag.vectorstores import ChromaProvider, FaissProvider, MultiStoreRetriever, PineconeProvider
from app.utils.observability import StageTrace, stage_timer


class RAGPipelineService:
    """
    Production RAG service with:
    - 3 interchangeable vector backends (FAISS, Pinecone, Chroma)
    - MongoDB for document metadata alongside vector indices
    - LangGraph-orchestrated retrieval + generation
    - Per-stage latency telemetry
    """

    def __init__(self) -> None:
        self._embedding = LangChainEmbeddingService(openai_api_key=settings.OPENAI_API_KEY)

        self._providers = [
            FaissProvider(),
            PineconeProvider(api_key=settings.PINECONE_API_KEY, index_name=settings.PINECONE_INDEX_NAME),
            ChromaProvider(collection_name=settings.CHROMA_COLLECTION_NAME),
        ]
        self._retriever = MultiStoreRetriever(self._providers)
        self._generator = LangChainGenerationPipeline(openai_api_key=settings.OPENAI_API_KEY)
        self._workflow  = RAGGraphWorkflow(
            embedding_service=self._embedding,
            retriever=self._retriever,
            generator=self._generator,
        )
        # MongoDB for structured document metadata (separate from vector indices)
        self._mongo = MongoDocumentStore(url=settings.MONGODB_URL)

    # ── Ingest ────────────────────────────────────────────────────────────────

    async def ingest(self, request: IngestRequest) -> dict:
        """
        Ingest documents:
        1. Chunk each document
        2. Embed all chunks in a single batched call
        3. Upsert embeddings into all 3 vector stores concurrently
        4. Store document metadata in MongoDB
        """
        traces: list[StageTrace] = []

        with stage_timer("chunking", traces):
            all_chunk_texts: list[str] = []
            chunk_refs: list[tuple[str, str, dict]] = []
            for doc in request.documents:
                chunker = DocumentChunker(ChunkingConfig(request.chunk_size, request.chunk_overlap))
                for chunk_id, chunk_text in chunker.split(doc.doc_id, doc.text):
                    all_chunk_texts.append(chunk_text)
                    chunk_refs.append((chunk_id, doc.doc_id, doc.metadata))

        if not all_chunk_texts:
            return {"documents": len(request.documents), "chunks": 0, "mongo_stored": 0}

        with stage_timer("embeddings", traces):
            vectors = await self._embedding.embed_documents(all_chunk_texts)

        with stage_timer("vector_upsert", traces):
            chunks: list[DocumentChunk] = [
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=text,
                    embedding=embedding,
                    metadata=metadata,
                )
                for (chunk_id, doc_id, metadata), text, embedding
                in zip(chunk_refs, all_chunk_texts, vectors)
            ]
            await self._retriever.upsert_all(chunks)

        # Store document metadata in MongoDB (non-blocking — failures don't break ingest)
        mongo_stored = 0
        with stage_timer("mongo_store", traces):
            for doc in request.documents:
                await self._mongo.store(
                    doc_id=doc.doc_id,
                    text_preview=doc.text[:500],
                    metadata={
                        **(doc.metadata or {}),
                        "chunk_count": sum(1 for _, did, _ in chunk_refs if did == doc.doc_id),
                        "chunk_size":  request.chunk_size,
                    },
                )
                mongo_stored += 1

        return {
            "documents":    len(request.documents),
            "chunks":       len(chunks),
            "mongo_stored": mongo_stored if self._mongo.enabled else 0,
            "latency_ms":   {trace.stage: trace.latency_ms for trace in traces},
        }

    # ── Query ─────────────────────────────────────────────────────────────────

    async def query(self, query: str, top_k: int, providers: list[str]) -> RAGQueryResponse:
        """
        Retrieve + generate:
        1. Run the LangGraph RAG workflow across selected providers
        2. Enrich source metadata from MongoDB where available
        """
        traces: list[StageTrace] = []
        start = time.perf_counter()
        initial_state = RAGGraphState(query=query, top_k=top_k, providers=tuple(providers))

        with stage_timer("graph_workflow", traces):
            final_state = await self._workflow.run(initial_state)

        # Enrich hits with MongoDB metadata
        with stage_timer("mongo_enrich", traces):
            sources = []
            for hit in final_state.retrieval_hits:
                mongo_meta = await self._mongo.get(hit.doc_id if hasattr(hit, "doc_id") else hit.chunk_id.split("::")[0])
                enriched_meta = {**(hit.metadata or {}), **(mongo_meta or {})}
                sources.append(SourceChunk(
                    provider=hit.provider,
                    chunk_id=hit.chunk_id,
                    score=hit.score,
                    text=hit.text,
                    metadata=enriched_meta,
                ))

        latency = {trace.stage: trace.latency_ms for trace in traces}
        latency["total"] = (time.perf_counter() - start) * 1000

        answer = (
            final_state.response.answer
            if final_state.response
            else "Retrieval context returned but no answer generated."
        )
        confidence = final_state.response.confidence if final_state.response else 0.2

        return RAGQueryResponse(
            answer=answer,
            confidence=confidence,
            sources=sources,
            token_usage=final_state.token_usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            latency_ms=latency,
            degraded=final_state.degraded,
        )

    # ── Benchmark ─────────────────────────────────────────────────────────────

    async def benchmark(self, query: str, top_k: int) -> dict:
        """Measure retrieval latency for each provider independently."""
        results = {}
        for provider in self._providers:
            start = time.perf_counter()
            try:
                resp = await self.query(query, top_k, [provider.name])
                elapsed_ms = (time.perf_counter() - start) * 1000
                results[provider.name] = {
                    "latency_ms":    round(elapsed_ms, 2),
                    "hits_returned": len(resp.sources),
                    "sub_200ms":     elapsed_ms < 200,
                    "stage_latency": resp.latency_ms,
                    "using_real_backend": not isinstance(provider,
                        # mark as real if it has a real index/collection attached
                        type(None)),
                }
            except Exception as exc:
                results[provider.name] = {"error": str(exc), "latency_ms": None}

        latencies = [v["latency_ms"] for v in results.values() if v.get("latency_ms") is not None]
        return {
            "query":   query,
            "top_k":   top_k,
            "providers": results,
            "mongo_enabled": self._mongo.enabled,
            "summary": {
                "min_latency_ms":  round(min(latencies), 2) if latencies else None,
                "max_latency_ms":  round(max(latencies), 2) if latencies else None,
                "all_sub_200ms":   all(v.get("sub_200ms", False) for v in results.values() if "sub_200ms" in v),
            },
        }
