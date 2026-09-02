# Wardrobe AI — Outfit Recommendation Engine + 3D Frontend

A full-stack, AI-powered wardrobe assistant. Combines an optimized graph-based outfit recommendation engine (Stage 1), a modern FastAPI/PostgreSQL/Redis backend (Stage 2), and an interactive Next.js + React Three Fiber frontend with a procedural 3D avatar viewer and animated particle field (Stage 3).

---

## 🚀 Architecture Overview

```text
Next.js Frontend (Stage 3)
  ├── Interactive Particle Field (Canvas / rAF)
  ├── Wardrobe Browser + Recommendation UI
  └── React Three Fiber — 3D Avatar Viewer
             │
             ▼ HTTP (localhost:8000/api/v1)
FastAPI Backend (Stage 2)
             │
             ▼
  Services (WardrobeService, RecommendationService)
     │                        │
     ▼                        ▼
PostgreSQL (SQLAlchemy)   Stage 1 Graph Engine
                          (Branch & Bound Searcher)
     │                        │
     ▼                        ▼
Persistence             Recommendation Output
         ▲             ▲
         └─── Redis ───┘
          (Cache-Aside)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| 3D Viewer | React Three Fiber, `@react-three/drei`, Three.js |
| Particles | HTML Canvas + `requestAnimationFrame` (no DOM elements) |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL + SQLAlchemy ORM + Alembic |
| Cache | Redis (Cache-Aside pattern) |
| Engine | Branch & Bound graph search, cosine similarity scoring |

---

## 📦 Prerequisites

Make sure you have the following installed:

- **Python 3.10+**
- **Node.js 20+** and **npm 10+**
- **PostgreSQL** (running on `localhost:5432`)
- **Redis** (running on `localhost:6379`)

---

## ⚙️ Backend Setup

### 1. Create & activate a Python virtual environment

```bash
cd d:\Swaroop Personal\Wardrobe\wardrobe_automation

python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.venv\Scripts\activate.bat

# macOS / Linux:
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example `.env` and update credentials:

```bash
cp .env.example .env
```

Default values that should work with a local Postgres/Redis:

```env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wardrobe
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=3600
CACHE_ENABLED=True
```

### 4. Run database migrations

```bash
cd backend
python -m alembic upgrade head
cd ..
```

### 5. Import initial wardrobe data from CSV

```bash
python backend/scripts/import_csv.py
```

### 6. Start the FastAPI server

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be live at:
- **API Base**: http://localhost:8000/api/v1
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🖥️ Frontend Setup (Stage 3)

Open a **new terminal** (keep the backend running).

### 1. Install frontend dependencies

```bash
cd frontend
npm install
```

### 2. Start the Next.js dev server

```bash
npm run dev
```

Frontend will be live at: **http://localhost:3000**

> **Note:** The frontend proxies API calls to `http://localhost:8000/api/v1`. Make sure the backend is running before loading the UI.

---

## 🎮 Using the App

Once both servers are running:

1. Open **http://localhost:3000** in your browser.
2. The **left panel** shows your wardrobe and the recommendation action.
3. Click **"Recommend Best Outfit"** — the engine runs Branch & Bound and returns the highest-scored outfit.
4. The **3D avatar** in the right panel updates its clothing colors to match the recommended outfit.
5. **Drag to rotate**, **scroll to zoom** the avatar.
6. Move your cursor over the left panel to interact with the **ambient particle field**.

---

## 📡 API Reference

### Wardrobe Items (`/api/v1/wardrobe/items`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/wardrobe/items` | List all items (`?type=shirt`, `?category=tops`) |
| `GET` | `/api/v1/wardrobe/items/{id}` | Get a single item |
| `POST` | `/api/v1/wardrobe/items` | Create a new item |
| `PUT` | `/api/v1/wardrobe/items/{id}` | Update an item |
| `DELETE` | `/api/v1/wardrobe/items/{id}` | Delete an item |

### Recommendations (`/api/v1/recommendations`)

```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "required_types": ["shirt", "pants", "shoes", "jacket"],
    "strategy": "best",
    "formality": 7.0,
    "vibes": ["clean", "minimal"]
  }'
```

---

## 🧪 Running Tests & Benchmarks

### Backend tests (pytest)

```bash
pytest -v
```

### Stage 1 scaling benchmarks

```bash
python -m benchmarks.benchmark_stage1
```

---

## 🌟 Stage 3 Feature: Interactive Particle Field

The left panel background features a canvas-based ambient particle field:

- **At rest** — calm indigo/purple dots float with gentle sine-wave drift.
- **Cursor moves** — nearby particles repel with smooth spring physics and distance-based falloff.
- **Cursor stops** — particles gradually settle back.
- **Cursor leaves** — ambient drift resumes.
- **Mobile** — reduced particle density, touch-only (no cursor).
- **`prefers-reduced-motion`** — particles are static, no animation.

The canvas uses `pointer-events: none` — all UI elements remain fully clickable.

---

## 🗂️ Project Structure

```text
wardrobe_automation/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/routes/          # wardrobe.py, recommendations.py, legacy.py
│   │   ├── core/                # scoring/, graph/, recommendation/
│   │   ├── models/wardrobe.py   # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic layer
│   │   └── db/                  # Database connection
│   ├── migrations/              # Alembic migration files
│   └── scripts/import_csv.py    # CSV import utility
├── frontend/
│   └── src/
│       ├── app/                 # Next.js App Router pages
│       ├── components/
│       │   ├── WardrobeApp.tsx  # Main app component
│       │   ├── 3d/
│       │   │   └── AvatarViewer.tsx        # React Three Fiber 3D viewer
│       │   └── effects/
│       │       └── InteractiveParticleField.tsx  # Canvas particle system
│       └── lib/api.ts           # FastAPI client (fetch)
├── benchmarks/benchmark_stage1.py
├── tests/
├── data/
└── requirements.txt
```