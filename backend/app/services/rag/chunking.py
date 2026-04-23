from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChunkingConfig:
    """Configuration for deterministic text splitting."""

    chunk_size: int = 500
    chunk_overlap: int = 80


class DocumentChunker:
    """Simple explicit chunking strategy with overlap."""

    def __init__(self, config: ChunkingConfig) -> None:
        self._config = config

    def split(self, doc_id: str, text: str) -> list[tuple[str, str]]:
        """Split one document into chunk_id/text tuples."""

        if not text.strip():
            return []

        chunks: list[tuple[str, str]] = []
        start = 0
        index = 0
        while start < len(text):
            end = min(start + self._config.chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append((f"{doc_id}:{index}", chunk_text))
            if end == len(text):
                break
            start = max(0, end - self._config.chunk_overlap)
            index += 1
        return chunks
