from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from app.services.llm.langchain_pipeline import LLMResponse
from app.services.rag.base import RetrievalHit
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.vectorstores import MultiStoreRetriever

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # noqa: BLE001
    END = "END"
    START = "START"
    StateGraph = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class RAGGraphState:
    """Immutable workflow state used for retries and rollback."""

    query: str
    top_k: int
    providers: tuple[str, ...]
    retries: int = 0
    max_retries: int = 2
    retrieval_hits: tuple[RetrievalHit, ...] = ()
    response: LLMResponse | None = None
    token_usage: dict[str, int] | None = None
    degraded: bool = False
    last_error: str | None = None


class RAGGraphWorkflow:
    """LangGraph-orchestrated RAG flow with conditional retry routing."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        retriever: MultiStoreRetriever,
        generator: Any,
    ) -> None:
        self._embedding_service = embedding_service
        self._retriever = retriever
        self._generator = generator

        self._compiled = self._build_graph() if StateGraph else None

    async def run(self, state: RAGGraphState) -> RAGGraphState:
        """Run workflow using LangGraph when available, else use direct fallback."""

        if self._compiled is not None:
            final_state = await self._compiled.ainvoke(state)
            return final_state

        try:
            retrieval_state = await self._retrieve(state)
            generated_state = await self._generate(retrieval_state)
            return await self._validate(generated_state)
        except Exception as exc:  # noqa: BLE001
            return replace(state, degraded=True, last_error=str(exc))

    def _build_graph(self) -> Any:
        graph = StateGraph(RAGGraphState)

        graph.add_node("retrieve", self._retrieve)
        graph.add_node("generate", self._generate)
        graph.add_node("validate", self._validate)
        graph.add_node("rollback", self._rollback)

        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "generate")
        graph.add_edge("generate", "validate")
        graph.add_conditional_edges(
            "validate",
            self._route_after_validate,
            {
                "success": END,
                "retry": "rollback",
                "degraded": END,
            },
        )
        graph.add_edge("rollback", "retrieve")

        return graph.compile()

    async def _retrieve(self, state: RAGGraphState) -> RAGGraphState:
        query_embedding = await self._embedding_service.embed_query(state.query)
        hits = await self._retriever.retrieve(query_embedding, state.top_k, list(state.providers))
        return replace(state, retrieval_hits=tuple(hits))

    async def _generate(self, state: RAGGraphState) -> RAGGraphState:
        response, token_usage = await self._generator.generate(state.query, list(state.retrieval_hits))
        return replace(state, response=response, token_usage=token_usage)

    async def _validate(self, state: RAGGraphState) -> RAGGraphState:
        if state.response and state.response.confidence >= 0.35:
            return state
        if state.retries >= state.max_retries:
            return replace(state, degraded=True, last_error="Low confidence after retries")
        return state

    async def _rollback(self, state: RAGGraphState) -> RAGGraphState:
        return replace(
            state,
            retries=state.retries + 1,
            retrieval_hits=(),
            response=None,
            token_usage=None,
            last_error="Retrying with rollback",
        )

    @staticmethod
    def _route_after_validate(state: RAGGraphState) -> str:
        if state.degraded:
            return "degraded"
        if state.response and state.response.confidence >= 0.35:
            return "success"
        return "retry"
