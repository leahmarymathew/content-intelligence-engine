# AI-Driven Content Intelligence Engine

AI-powered content generation platform with analytics, experiments, automation workflows, and a modern React + FastAPI stack.

## Tech Stack

- Frontend: React, Vite, Tailwind CSS, Recharts
- Backend: FastAPI, SQLAlchemy, JWT auth
- Database: SQLite (local), PostgreSQL (production)

## Project Structure

- `frontend/` React app
- `backend/` FastAPI API
- `ai_engine/` generation + prompt/classification utilities
- `analytics/` analytics utilities and SQL helpers
- `database/` models and seed scripts
- `docs/` architecture and API docs

## Local Setup

### 1) Backend

```powershell
cd backend
python -m venv venv
.\venv\bin\activate
pip install -r requirements.txt
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
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ENVIRONMENT=development
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