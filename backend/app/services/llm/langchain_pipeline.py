from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.services.rag.base import RetrievalHit
from app.utils.cache import AsyncTTLCache

try:
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
except Exception:  # noqa: BLE001
    JsonOutputParser = None  # type: ignore[assignment]
    ChatPromptTemplate = None  # type: ignore[assignment]
    ChatOpenAI = None  # type: ignore[assignment]


class LLMResponse(BaseModel):
    """Strict output schema from generation chain."""

    answer: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class LangChainGenerationPipeline:
    """LCEL chain with schema validation and query-level cache."""

    def __init__(self, openai_api_key: str, model_name: str = "gpt-4o-mini") -> None:
        self._token_cache: AsyncTTLCache[dict[str, int]] = AsyncTTLCache(ttl_seconds=900, max_items=5000)
        self._response_cache: AsyncTTLCache[LLMResponse] = AsyncTTLCache(ttl_seconds=300, max_items=2000)
        self._model = ChatOpenAI(model=model_name, api_key=openai_api_key, temperature=0.2) if openai_api_key and ChatOpenAI else None
        self._parser = JsonOutputParser(pydantic_object=LLMResponse) if JsonOutputParser else None

    async def generate(self, query: str, hits: list[RetrievalHit]) -> tuple[LLMResponse, dict[str, int]]:
        """Generate answer from query plus retrieved context."""

        cache_key = f"{query}|{','.join(hit.chunk_id for hit in hits)}"
        cached_response = await self._response_cache.get(cache_key)
        cached_tokens = await self._token_cache.get(cache_key)
        if cached_response and cached_tokens:
            return cached_response, cached_tokens

        context = "\n\n".join(f"[{hit.chunk_id}] {hit.text}" for hit in hits)

        if self._model and self._parser and ChatPromptTemplate:
            prompt = ChatPromptTemplate.from_template(
                """
You are a production-grade retrieval assistant.
Answer only from the provided context.
Return strict JSON with keys: answer, confidence.

Query: {query}
Context:
{context}

{format_instructions}
""".strip()
            )
            chain = prompt | self._model | self._parser
            result: dict[str, Any] = await chain.ainvoke(
                {
                    "query": query,
                    "context": context,
                    "format_instructions": self._parser.get_format_instructions(),
                }
            )
            if hasattr(LLMResponse, "model_validate"):
                validated = LLMResponse.model_validate(result)  # Pydantic v2
            else:
                validated = LLMResponse.parse_obj(result)  # Pydantic v1
            token_usage = {
                "prompt_tokens": max(1, len(context) // 4),
                "completion_tokens": max(1, len(validated.answer) // 4),
                "total_tokens": max(1, len(context) // 4) + max(1, len(validated.answer) // 4),
            }
        else:
            fallback_answer = "I could not call the external LLM provider, so this response uses retrieved context only. "
            fallback_answer += " ".join(hit.text[:120] for hit in hits[:2]) if hits else "No relevant context was found."
            validated = LLMResponse(answer=fallback_answer, confidence=0.45 if hits else 0.1)
            token_usage = {
                "prompt_tokens": max(1, len(context) // 4),
                "completion_tokens": max(1, len(validated.answer) // 4),
                "total_tokens": max(1, len(context) // 4) + max(1, len(validated.answer) // 4),
            }

        await self._response_cache.set(cache_key, validated)
        await self._token_cache.set(cache_key, token_usage)
        return validated, token_usage
