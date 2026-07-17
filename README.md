# Eurus AI Employee Copilot

A prototype AI assistant built from **Eurus Technologies'** public website and
documents, demonstrating RAG-grounded Q&A and agentic workflows (proposal
generation, email drafting, meeting summarization).

> Built as a technical demonstration using only publicly available
> information. Not an internal Eurus system.

See [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) for the full architecture,
module breakdown, and API contract.

## Quick start (local, no Docker)

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then fill in GROQ_API_KEY / OPENAI_API_KEY
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000` — interactive docs at `/docs`.

### 2. Ingest some public data

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://<eurus-website>/services"}'
```

Repeat for the about page, AI services page, case studies, etc.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env   # fill in your API key
docker compose up --build
```

## Project structure

```
eurus-ai-copilot/
├── backend/app/
│   ├── core/            # config, logging
│   ├── api/v1/           # FastAPI routes
│   ├── schemas/          # request/response models
│   └── services/
│       ├── ingestion/    # scraping + chunking
│       ├── llm/          # provider-agnostic OpenAI/Groq interface
│       ├── vectorstore/  # ChromaDB wrapper
│       ├── rag/          # retriever + grounded answers
│       ├── agents/       # proposal / email / meeting agents
│       └── pdf/          # PDF export
├── frontend/             # Next.js chat UI
└── docker-compose.yml
```

## Module design principle

Every module talks to others only through its public function/class —
never reaches into another module's internals. Swapping ChromaDB for
another vector DB, or OpenAI for Groq, means touching one file
(`vectorstore/chroma_store.py` or `services/llm/factory.py`), not the
whole codebase.

## Roadmap

- [ ] Wire LangGraph into `agents/orchestrator.py` for free-form task routing
- [ ] Add `/compare` endpoint (document diff)
- [ ] Add SOP/internal-doc assistant mode
- [ ] Record 2–3 min Loom demo
- [ ] Deploy backend + frontend, add live demo link here
