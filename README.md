# AI-Driven Content Intelligence Engine

AI-powered content generation platform with analytics, experiments, automation workflows, and a production-oriented FastAPI RAG backend.

## Tech Stack

- Frontend: React, Vite, Tailwind CSS, Recharts
- Backend: FastAPI (async), SQLAlchemy, JWT auth, LangChain LCEL, LangGraph
- Retrieval: FAISS, Pinecone, Chroma (provider-based architecture)
- Database: SQLite (local), PostgreSQL (production)

## Project Structure

- `frontend/` React app
- `backend/` FastAPI API
- `backend/app/api/v1/` versioned API routers
- `backend/app/services/rag/` chunking, embeddings, retrieval, graph workflow
- `backend/app/services/llm/` LCEL generation pipelines + parsers
- `backend/app/utils/` shared observability and caching utilities
- `ai_engine/` generation + prompt/classification utilities
- `analytics/` analytics utilities and SQL helpers
- `database/` models and seed scripts
- `docs/` architecture and API docs

## Production RAG Upgrade

The backend now includes a modular production-style RAG pipeline:

- Explicit chunking with configurable `chunk_size` and `chunk_overlap`
- Embedding pipeline with cache support and offline-safe fallback embeddings
- Multi-vector retrieval over FAISS/Pinecone/Chroma via provider abstractions
- LangChain LCEL response generation with strict Pydantic output validation
- LangGraph orchestration with nodes, conditional routing, retries, and rollback state
- Async API execution for ingestion and query routes
- Structured JSON logging + stage latency tracing + request latency headers

### New API Endpoints

- `POST /api/v1/rag/ingest`
- `POST /api/v1/rag/query`

## Local Setup

### 1) Backend

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

### 2) Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL=sqlite:///./content.db
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=content-intelligence
CHROMA_COLLECTION_NAME=content-intelligence
RAG_DEFAULT_TOP_K=5
RAG_MAX_RETRIES=2
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
```

## Main API Routes

- `POST /auth/login`
- `POST /auth/token`
- `GET /auth/verify`
- `POST /generate-content`
- `GET /content-library`
- `GET /analytics`
- `GET /health`
- `POST /api/v1/rag/ingest`
- `POST /api/v1/rag/query`

## Async and Performance Notes

- Async helps most in network-bound and I/O-bound steps: multi-provider retrieval, LLM calls, and concurrent ingestion pipelines.
- Async is less helpful for pure CPU-heavy operations unless they are moved to worker pools or separate compute services.
- Existing synchronous DB calls in legacy endpoints are wrapped with threadpool offloading where updated.

## Observability and Debugging

- Request-level tracing middleware emits structured JSON logs.
- Stage-level latency tracking captures retrieval/generation workflow timings.
- Failure points are logged at API, retrieval, and generation boundaries.
- `X-Request-Latency-Ms` header is returned for API performance diagnostics.

## Testing

Run the focused backend tests for the production RAG upgrade:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests/test_retrieval.py tests/test_pipeline.py tests/test_rag_api.py -q
```

## Deployment

- Quick path: `QUICK_DEPLOY.md`
- Full guide: `DEPLOYMENT.md`
- Supported targets: Render/Railway/Fly.io (backend), Vercel (frontend), Supabase/Neon (database)

## Useful Scripts

- `scripts/deploy.ps1` (Windows)
- `scripts/deploy.sh` (Linux/macOS)

## Notes

- Authentication uses JWT.
- Password hashing is configured via passlib.
- CORS and other runtime settings are centralized in `backend/app/core/config.py`.
- RAG pipeline modules are organized for extension and provider swap without API changes.