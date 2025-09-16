# Customer Interview Analysis App

A full-stack application for analyzing customer interviews using React (frontend), FastAPI (backend), PostgreSQL (database), and Gemini API for LLM-powered analysis.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Features

- FastAPI backend with REST endpoints
- PostgreSQL persistence with SQLAlchemy
- Gemini API integration for interview analysis
- React + Vite + TypeScript frontend
- Dockerized dev environment

## Prerequisites

- Docker and Docker Compose (recommended), or
- Python 3.11+, Node.js 18+

## Environment Variables

Create environment files based on examples below.

- Backend (`backend/.env.example`):
  - `DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/interviews`
  - `BACKEND_CORS_ORIGINS=http://localhost:5173`
  - `GEMINI_API_KEY=your_gemini_api_key_here`
  - `GEMINI_MODEL=gemini-1.5-flash`

- Frontend (`frontend/.env.example`):
  - `VITE_API_BASE_URL=http://localhost:8000`

## Quickstart (Docker)

1. Copy environment examples:
   - `cp backend/.env.example backend/.env`
   - `cp frontend/.env.example frontend/.env`
2. Start services:
   - `docker compose up --build`
3. Access:
   - Frontend: `http://localhost:5173`
   - Backend docs: `http://localhost:8000/docs`

## Run Backend only (Docker)

If you want just the API running (no frontend):

1. Copy env file:
   - `cp backend/.env.example backend/.env`
2. Start Postgres and Backend:
   - `docker compose up -d db backend`
3. Verify:
   - `curl http://localhost:8000/health` → `{ "status": "ok" }`
   - Open `http://localhost:8000/docs`

## Local Development (without Docker)

### Backend

Choose one of the following to install dependencies.

Using uv (fast, recommended):
- `cd backend`
- `uv venv && source .venv/bin/activate`
- `uv sync`  # installs from `pyproject.toml`

Using pip:
- `cd backend`
- `python -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`

Then configure environment:
- `cp .env.example .env`
- Set `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/interviews`
- Optionally set `BACKEND_CORS_ORIGINS=http://localhost:5173` to allow the Vite dev server
- Set `GEMINI_API_KEY` if you want analyses to run; without it, `analysis` may be `null`

Set up local PostgreSQL (one-time):
- Docker (quick local DB):
  - `docker run --name interview_db_local -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=interviews -p 5432:5432 -d postgres:15`
- Or use your native Postgres and ensure it matches the `DATABASE_URL`.

Run database migrations (Alembic):
- Generate initial migration (autogenerate):
  - `alembic revision --autogenerate -m "init"`
- Apply migrations:
  - `alembic upgrade head`

Run the server (from `backend/` directory):
- `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

Verify endpoints:
- `curl http://localhost:8000/health` → `{ "status": "ok" }`
- `curl http://localhost:8000/api/v1/interviews` → `[]` (HTTP 200)
- Open API docs: `http://localhost:8000/docs`

Troubleshooting:
- CORS: make sure `BACKEND_CORS_ORIGINS` includes `http://localhost:5173` (or your frontend origin). The backend already installs CORS middleware via `CORSMiddleware`.
- 404s: confirm you are requesting paths under the API prefix (e.g., `/api/v1/interviews`). Health check is at `/health`.
- Database connection errors: verify Postgres is running and `DATABASE_URL` is correct.

### Frontend

1. Install deps:
   - `cd frontend && npm install`
2. Run dev server:
   - `npm run dev`

## API Overview

- `GET /health` – liveness
- `POST /api/v1/interviews` – create an interview, analyze transcript via Gemini
- `POST /api/v1/interviews/upload` – create from uploaded files (PDF/TXT)
- `GET /api/v1/interviews` – list interviews
- `GET /api/v1/interviews/{id}` – get single interview

OpenAPI docs available at `/docs`.

## Notes

- The backend initializes DB tables on startup for convenience. Migrations (Alembic) can be added as the schema evolves.
- Keep your `GEMINI_API_KEY` secret. Do not commit `.env` files.
