from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rag_ingest_and_query_api() -> None:
    ingest_payload = {
        "documents": [
            {
                "doc_id": "api-doc-1",
                "text": "Chroma and FAISS can be used as vector stores in a RAG pipeline.",
                "metadata": {"source": "api-test"},
            }
        ],
        "chunk_size": 140,
        "chunk_overlap": 20,
    }

    ingest_response = client.post("/api/v1/rag/ingest", json=ingest_payload)
    assert ingest_response.status_code == 200
    assert ingest_response.json()["chunks"] >= 1

    query_response = client.post(
        "/api/v1/rag/query",
        json={
            "query": "Which vector stores are configured?",
            "top_k": 3,
            "use_providers": ["faiss", "chroma", "pinecone"],
        },
    )
    assert query_response.status_code == 200
    body = query_response.json()
    assert "answer" in body
    assert "token_usage" in body
