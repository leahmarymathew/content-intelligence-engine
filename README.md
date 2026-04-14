# Quill

AI-powered content platform for B2B marketing teams. Generate audience-targeted content, run A/B experiments, track performance analytics, and automate content workflows — backed by a production RAG pipeline with three interchangeable vector backends and MongoDB document metadata.

**[Live Demo](https://quill-app.vercel.app) · [API Docs](https://quill-api.onrender.com/docs)**

---

## What it does

| Feature | Description |
|---|---|
| **Content generation** | Llama 3.3 70B (via Groq) generates blog posts, emails, case studies, newsletters, and social posts using structured prompt templates per content type |
| **RAG pipeline** | Documents ingested → chunked → embedded → upserted into FAISS, Pinecone, and Chroma simultaneously. Queries run concurrently across all providers, results merged and score-normalised |
| **MongoDB metadata** | Structured document metadata (title, source, chunk count) stored in MongoDB alongside vector indices enabling hybrid structured + unstructured retrieval |
| **A/B experiments** | Full lifecycle: create hypothesis → configure traffic split → track impressions and conversions via API → live metrics updated in real time |
| **Analytics** | Engagement rate, CTR, AI accuracy score, and per-category breakdown — all from live database records |
| **Automation** | Event-driven and scheduled workflow definitions (CMS publish, Slack alerts, CRM tagging) with pause/resume |

---

## Tech stack

**Backend**
- Python 3.12, FastAPI (async), SQLAlchemy 2.0, JWT auth
- LangChain LCEL, LangGraph workflow orchestration
- OpenAI embeddings (cached, pseudo-embedding fallback)

**Vector stores** — provider-swappable via shared abstract interface
- FAISS — `IndexIDMap(IndexFlatIP)` with L2-normalised cosine similarity
- Pinecone — real index when `PINECONE_API_KEY` present, in-memory fallback otherwise
- Chroma — local `chromadb` client with `hnsw:space=cosine`

**Metadata & storage**
- MongoDB via Motor (async) — RAG document metadata alongside vector indices
- PostgreSQL (production) / SQLite (local) via SQLAlchemy

**LLM**
- Groq API — Llama 3.3 70B for content generation

**Frontend**
- React 19, Vite, Tailwind CSS v4, Recharts

---

## RAG architecture

```
POST /api/v1/rag/ingest
  ├── DocumentChunker      configurable chunk_size + overlap
  ├── EmbeddingService     batched, TTL-cached, offline-safe fallback
  ├── MultiStoreRetriever  concurrent upsert to FAISS + Pinecone + Chroma
  └── MongoDocumentStore   metadata upserted alongside vectors

POST /api/v1/rag/query
  └── RAGGraphWorkflow (LangGraph)
       ├── embed_query      vectorise the user query
       ├── retrieve         concurrent search across providers, deduped + normalised
       ├── generate         LangChain LCEL → Pydantic-validated JSON output
       └── fallback         degraded mode returns retrieval context if generation fails
  └── MongoDB enrichment    hit metadata enriched from document store
  └── Stage latency tracing per-node timing in response
```

Benchmark individual provider latency: `GET /api/v1/rag/benchmark`

---

## Local setup

### Backend

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Seed sample content and engagement data:

```bash
python -m app.seed
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment variables

`backend/.env`

```env
# Required
GROQ_API_KEY=gsk_...

# Database
DATABASE_URL=sqlite:///./content.db          # or postgresql:// for production

# Optional — vector backends (fallback to in-memory without these)
OPENAI_API_KEY=sk-...                         # for real embeddings
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=quill-content
CHROMA_COLLECTION_NAME=quill-content

# Optional — MongoDB metadata store
MONGODB_URL=mongodb+srv://...

# Auth + server
SECRET_KEY=change-this-in-production
CORS_ORIGINS=http://localhost:5173
```

`frontend/.env`

```env
VITE_API_URL=http://localhost:8000
```

---

## API reference

### Content
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/generate-content` | Generate content via Groq LLM |
| `GET` | `/content-library` | List all content with category |
| `GET` | `/content/{id}` | Get single item |

### RAG
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/rag/ingest` | Ingest documents into all vector stores + MongoDB |
| `POST` | `/api/v1/rag/query` | Retrieve + generate across selected providers |
| `GET` | `/api/v1/rag/benchmark` | Per-provider latency benchmark |
| `GET` | `/api/v1/rag/mongo/status` | MongoDB health check |
| `GET` | `/api/v1/rag/mongo/documents` | List documents in MongoDB |

### Experiments
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/experiments` | All experiments with live metrics |
| `POST` | `/experiments` | Create experiment |
| `PATCH` | `/experiments/{id}/status` | Launch / Pause / Complete |
| `POST` | `/experiments/{id}/track` | Record impression or conversion |

### Analytics & Auth
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics` | Engagement, CTR, accuracy, category breakdown |
| `POST` | `/auth/login` | Get JWT token |
| `GET` | `/health` | Health check |

---

## Tests

```bash
cd backend
python -m pytest tests/ -v
```

- `test_retrieval.py` — verifies ranking order across all 3 vector providers
- `test_pipeline.py` — end-to-end ingest → query with latency assertions
- `test_rag_api.py` — HTTP-level API tests

---

## Deployment

See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for a step-by-step guide.

**Frontend → Vercel**
- Root dir: `frontend`, build: `npm run build`, output: `dist`
- Env: `VITE_API_URL=https://your-backend.onrender.com`

**Backend + DB → Render**
- `render.yaml` included — auto-provisions web service + PostgreSQL
- Add `GROQ_API_KEY` and `CORS_ORIGINS` in Render environment dashboard
