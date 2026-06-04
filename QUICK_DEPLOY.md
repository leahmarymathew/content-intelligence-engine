# Quick Deploy Guide

Deploy the full stack for free in ~20 minutes using Render (backend + PostgreSQL) and Vercel (frontend).

---

## 1. Push to GitHub

```bash
git add .
git commit -m "chore: ready for deployment"
git push origin main
```

---

## 2. Deploy backend + database on Render

The project includes a `render.yaml` that auto-configures everything.

1. Go to **render.com** → sign up with GitHub
2. Click **New** → **Blueprint** → connect your repo
3. Render reads `render.yaml` and creates:
   - A Python web service (`ai-content-intelligence-backend`)
   - A free PostgreSQL database (`ai-content-db`)
4. Once deployed, go to your web service → **Environment** and add:
   - `GROQ_API_KEY` → your key from **console.groq.com** (free)
   - `CORS_ORIGINS` → your Vercel frontend URL (set after step 3)

Your backend URL: `https://ai-content-intelligence-backend.onrender.com`

---

## 3. Deploy frontend on Vercel

1. Go to **vercel.com** → sign up with GitHub
2. Click **Add New Project** → import your repo
3. Set build settings:
   - **Root Directory:** `frontend`
   - **Framework:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add environment variable:
   - `VITE_API_URL` → your Render backend URL from step 2

Your frontend URL: `https://your-app.vercel.app`

---

## 4. Connect frontend ↔ backend

Go back to **Render** → your web service → **Environment** → update `CORS_ORIGINS`:

```
https://your-app.vercel.app
```

Render redeploys automatically on save.

---

## 5. Seed the database

Run once after the backend is live, using the external database URL from Render dashboard:

```powershell
$env:DATABASE_URL = "postgresql://..."   # Render → database → External URL
cd backend
../.venv/Scripts/python.exe -m app.seed
```

---

## Cost

| Service | Free tier |
|---|---|
| Vercel (frontend) | 100 GB/month, unlimited deploys |
| Render (backend) | Spins down after 15 min idle — first request ~30s cold start |
| Render PostgreSQL | 1 GB, expires after 90 days |

Upgrade backend to Render Starter ($7/month) to eliminate cold starts.

---

See [README.md](README.md) for full API reference and architecture details.
