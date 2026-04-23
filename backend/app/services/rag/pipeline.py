from __future__ import annotations

import time

from app.core.config import settings
from app.schemas.rag_schema import IngestRequest, RAGQueryResponse, SourceChunk
from app.services.llm.langchain_pipeline import LangChainGenerationPipeline
from app.services.rag.base import DocumentChunk
from app.services.rag.chunking import ChunkingConfig, DocumentChunker
from app.services.rag.embeddings import LangChainEmbeddingService
from app.services.rag.langgraph_workflow import RAGGraphState, RAGGraphWorkflow
from app.services.rag.vectorstores import ChromaProvider, FaissProvider, MultiStoreRetriever, PineconeProvider
from app.utils.observability import StageTrace, stage_timer


class RAGPipelineService:
    """Production-style RAG service with chunking, retrieval and generation."""

    def __init__(self) -> None:
        self._embedding = LangChainEmbeddingService(openai_api_key=settings.OPENAI_API_KEY)
        self._providers = [
            FaissProvider(),
            PineconeProvider(api_key=settings.PINECONE_API_KEY, index_name=settings.PINECONE_INDEX_NAME),
            ChromaProvider(collection_name=settings.CHROMA_COLLECTION_NAME),
        ]
        self._retriever = MultiStoreRetriever(self._providers)
        self._generator = LangChainGenerationPipeline(openai_api_key=settings.OPENAI_API_KEY)
        self._workflow = RAGGraphWorkflow(
            embedding_service=self._embedding,
            retriever=self._retriever,
            generator=self._generator,
        )

    async def ingest(self, request: IngestRequest) -> dict[str, int]:
        """Ingest documents using explicit chunking and batched embeddings."""

        traces: list[StageTrace] = []
        with stage_timer("chunking", traces):
            all_chunk_texts: list[str] = []
            chunk_refs: list[tuple[str, str, dict[str, object]]] = []
            for doc in request.documents:
                chunker = DocumentChunker(ChunkingConfig(request.chunk_size, request.chunk_overlap))
                for chunk_id, chunk_text in chunker.split(doc.doc_id, doc.text):
                    all_chunk_texts.append(chunk_text)
                    chunk_refs.append((chunk_id, doc.doc_id, doc.metadata))

        if not all_chunk_texts:
            return {"documents": len(request.documents), "chunks": 0}

        with stage_timer("embeddings", traces):
            vectors = await self._embedding.embed_documents(all_chunk_texts)

        with stage_timer("upsert", traces):
            chunks: list[DocumentChunk] = []
            for (chunk_id, doc_id, metadata), text, embedding in zip(chunk_refs, all_chunk_texts, vectors):
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=doc_id,
                        text=text,
                        embedding=embedding,
                        metadata=metadata,
                    )
                )
            await self._retriever.upsert_all(chunks)

        return {
            "documents": len(request.documents),
            "chunks": len(chunks),
        }

    async def query(self, query: str, top_k: int, providers: list[str]) -> RAGQueryResponse:
        """Execute full retrieval+generation flow with stage-level latency telemetry."""

        traces: list[StageTrace] = []
        start = time.perf_counter()
        initial_state = RAGGraphState(query=query, top_k=top_k, providers=tuple(providers))

        with stage_timer("graph_workflow", traces):
            final_state = await self._workflow.run(initial_state)

        latency = {trace.stage: trace.latency_ms for trace in traces}
        latency["total"] = (time.perf_counter() - start) * 1000

        sources = [
            SourceChunk(
                provider=hit.provider,
                chunk_id=hit.chunk_id,
                score=hit.score,
                text=hit.text,
                metadata=hit.metadata,
            )
            for hit in final_state.retrieval_hits
        ]

        answer = (
            final_state.response.answer
            if final_state.response
            else "I could not generate a full answer, but I returned the best retrieval context available."
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
