# Content Intelligence Engine

AI-powered content platform with a production RAG backend supporting 3 interchangeable vector stores, MongoDB document metadata, async FastAPI serving, and a React dashboard for content generation, A/B experiments, and analytics.

**[Live Demo](https://your-app.vercel.app) · [API Docs](https://your-backend.onrender.com/docs)**

---

## What it does

| Layer | What's built |
|---|---|
| **Content generation** | Groq (Llama 3.3 70B) generates blog posts, emails, case studies, social posts via structured prompt templates |
| **RAG pipeline** | Documents ingested → chunked → embedded → stored across FAISS + Pinecone + Chroma simultaneously. Queries run concurrently across all providers, results merged and score-normalised |
| **MongoDB metadata store** | Document metadata (title, source, chunk count) stored in MongoDB alongside vector indices for hybrid structured/unstructured retrieval |
| **A/B experiments** | Full experiment lifecycle: create hypothesis → set traffic split → track impressions/conversions via `POST /experiments/{id}/track` → live metrics |
| **Analytics** | Engagement, CTR, AI accuracy metrics pulled from PostgreSQL with per-category breakdown |
| **Automation** | Event-driven and scheduled workflow definitions with pause/resume |

---

## Tech stack

- **Backend:** Python 3.12, FastAPI (async), SQLAlchemy, JWT auth
- **AI/RAG:** LangChain LCEL, LangGraph orchestration, OpenAI embeddings
- **Vector stores:** FAISS (IndexIDMap + cosine), Pinecone, Chroma — provider-swappable via shared interface
- **Metadata store:** MongoDB via Motor (async) alongside vector indices
- **LLM:** Groq API (Llama 3.3 70B) for content generation
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Frontend:** React 19, Vite, Tailwind CSS v4, Recharts

---

## RAG architecture

```
POST /api/v1/rag/ingest
  └─ DocumentChunker (configurable chunk_size + overlap)
  └─ LangChainEmbeddingService (cached, offline-safe fallback)
  └─ MultiStoreRetriever.upsert_all()
       ├─ FaissProvider    → IndexIDMap(IndexFlatIP) — cosine similarity
       ├─ PineconeProvider → real index when API key present, in-memory fallback otherwise
       └─ ChromaProvider   → local chromadb, hnsw:space=cosine
  └─ MongoDocumentStore.store() — metadata alongside vectors

POST /api/v1/rag/query
  └─ RAGGraphWorkflow (LangGraph)
       ├─ embed_query node
       ├─ retrieve node  → concurrent across selected providers, deduped + normalised
       ├─ generate node  → LangChain LCEL chain → Pydantic-validated JSON output
       └─ fallback node  → degraded mode if generation fails
  └─ MongoDB metadata enrichment on retrieval hits
  └─ Stage-level latency telemetry (chunking / embedding / retrieval / generation)
```

**Benchmark:** `GET /api/v1/rag/benchmark` measures retrieval latency per provider independently.

---

## Setup

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Seed sample data:
```powershell
python -m app.seed
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Environment variables (`backend/.env`)

```env
# Required
GROQ_API_KEY=gsk_...

# Database (SQLite default, PostgreSQL for production)
DATABASE_URL=sqlite:///./content.db

# Optional — RAG vector backends
OPENAI_API_KEY=sk-...          # for real embeddings (pseudo-embeddings used otherwise)
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=content-intelligence
CHROMA_COLLECTION_NAME=content-intelligence

# Optional — MongoDB metadata store
MONGODB_URL=mongodb+srv://...

# Auth + server
SECRET_KEY=change-this
CORS_ORIGINS=http://localhost:5173
```

---

## API reference

### Content
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/generate-content` | Generate content via Groq LLM |
| `GET` | `/content-library` | List all generated content |
| `GET` | `/content/{id}` | Get single content item |

### RAG
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/rag/ingest` | Ingest documents into all vector stores + MongoDB |
| `POST` | `/api/v1/rag/query` | Query with retrieval + generation |
| `GET` | `/api/v1/rag/benchmark` | Latency benchmark across all providers |
| `GET` | `/api/v1/rag/mongo/status` | MongoDB connection + document count |
| `GET` | `/api/v1/rag/mongo/documents` | List documents in MongoDB |

### Experiments
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/experiments` | List all experiments with live metrics |
| `POST` | `/experiments` | Create experiment |
| `PATCH` | `/experiments/{id}/status` | Launch / Pause / Complete |
| `POST` | `/experiments/{id}/track` | Record impression or conversion event |

### Analytics + Auth
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics` | Engagement, CTR, AI accuracy, category breakdown |
| `POST` | `/auth/login` | Get JWT token |
| `GET` | `/health` | Health check |

---

## Tests

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests/ -v
```

Key test coverage:
- `test_retrieval.py` — verifies ranking order across all 3 providers
- `test_pipeline.py` — end-to-end ingest → query with latency assertions
- `test_rag_api.py` — HTTP-level API tests

---

## Deployment

**Frontend → Vercel**
- Root dir: `frontend`, build: `npm run build`, output: `dist`
- Env var: `VITE_API_URL=https://your-backend.onrender.com`

**Backend + DB → Render**
- `render.yaml` included — deploys web service + PostgreSQL automatically
- Set `GROQ_API_KEY` and `CORS_ORIGINS` in Render environment dashboard
