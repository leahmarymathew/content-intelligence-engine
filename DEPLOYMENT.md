# Deployment Plan: Render + Pinecone (Backend Only)

This is a simple production deployment plan for the FastAPI backend using Render and Pinecone.

## 1) requirements.txt (correct dependencies)

Backend dependencies are in [backend/requirements.txt](backend/requirements.txt).

Key runtime packages:
- fastapi
- uvicorn[standard]
- sqlalchemy
- pydantic v2
- langchain, langchain-openai, langgraph
- pinecone
- faiss-cpu, chromadb (kept for local/provider parity)

## 2) main.py (production-ready FastAPI entry)

Production entrypoint is [backend/app/main.py](backend/app/main.py) and includes:
- async middleware for request tracing
- structured startup/shutdown logging
- global exception handler returning safe JSON
- CORS via environment config

Local production-like run:

```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## 3) Environment Variables Setup

Set these in Render service environment:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<db>
SECRET_KEY=<strong-random-secret>
OPENAI_API_KEY=<your-openai-key>
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_INDEX_NAME=content-intelligence
CHROMA_COLLECTION_NAME=content-intelligence
RAG_DEFAULT_TOP_K=5
RAG_MAX_RETRIES=2
CORS_ORIGINS=https://<your-frontend-domain>
LOG_LEVEL=INFO
ENVIRONMENT=production
PYTHON_VERSION=3.12.0
```

## 4) Exact Render Configuration

Use [render.yaml](render.yaml) (Blueprint deploy) with:

- rootDir: `backend`
- build command:

```bash
pip install --upgrade pip && pip install -r requirements.txt
```

- start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
```

Notes:
- `--workers 1` is recommended on Render free/starter plans for stability.
- Scale vertically/horizontally first, then tune worker count.

## 5) How to Connect Pinecone

1. Create a Pinecone project and API key.
2. Create an index named `content-intelligence` (or set your own name in `PINECONE_INDEX_NAME`).
3. Set `PINECONE_API_KEY` and `PINECONE_INDEX_NAME` in Render env vars.
4. Deploy backend.
5. Ingest docs:

```bash
curl -X POST "https://<your-render-service>.onrender.com/api/v1/rag/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{"doc_id": "d1", "text": "Your source text", "metadata": {"source": "seed"}}],
    "chunk_size": 500,
    "chunk_overlap": 80
  }'
```

6. Query RAG:

```bash
curl -X POST "https://<your-render-service>.onrender.com/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in the document?",
    "top_k": 5,
    "use_providers": ["pinecone", "faiss", "chroma"]
  }'
```

## 6) How to Test Deployed API

Health check:

```bash
curl https://<your-render-service>.onrender.com/health
```

RAG query smoke test:

```bash
curl -X POST "https://<your-render-service>.onrender.com/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","top_k":3,"use_providers":["pinecone"]}'
```

Expected:
- HTTP 200 response
- JSON fields: `answer`, `confidence`, `sources`, `token_usage`, `latency_ms`, `degraded`
- Response header: `X-Request-Latency-Ms`

## 7) Common Errors and Fixes

1. `ModuleNotFoundError` during build
- Cause: wrong dependency versions or missing package in requirements.
- Fix: confirm [backend/requirements.txt](backend/requirements.txt) matches repository state and redeploy.

2. `422 Unprocessable Entity` on RAG endpoints
- Cause: invalid request body shape.
- Fix: match schema exactly (`documents`, `query`, `top_k`, `use_providers`).

3. Pinecone returns auth/index errors
- Cause: invalid `PINECONE_API_KEY` or wrong `PINECONE_INDEX_NAME`.
- Fix: verify key, region/project, and index existence.

4. CORS failures from frontend
- Cause: frontend domain not listed.
- Fix: set `CORS_ORIGINS` to your real frontend URL.

5. Render timeout/cold start issues
- Cause: free tier cold starts and heavy first request.
- Fix: keep service warm (scheduled ping), reduce payload size, and validate with `/health` first.

## Async + Logging + Error Handling Status

Already configured in code:
- Async route handlers and async middleware
- Structured logging via observability utilities
- Global exception safety handler in [backend/app/main.py](backend/app/main.py)
- Stage-level latency tracing in RAG pipeline

No Docker is required for this deployment path.
