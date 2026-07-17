# Eurus AI Employee Copilot — System Design

## 1. Goal
A custom AI assistant demo built specifically for a target company (starting with Eurus
Technologies), showing recruiters a working product instead of a resume line. Built from
public data only (website, public PDFs, blogs).

## 2. Modules (bounded contexts)

| Module | Responsibility | Owns |
|---|---|---|
| `ingestion` | Pull public data (website pages, PDFs), clean, chunk | scraper, chunker, loaders |
| `embeddings` | Turn chunks into vectors, manage the embedding model | provider-agnostic embedder |
| `vectorstore` | Store/query vectors (ChromaDB) | collection management, similarity search |
| `rag` | Retrieve relevant chunks + build grounded answers with citations | retriever, prompt builder |
| `agents` | Multi-step tasks: proposal generation, email drafting, meeting summarizing | orchestrator + per-task agents |
| `llm` | Single abstraction over OpenAI / Gemini / Groq so provider is swappable | provider interface |
| `pdf` | Export proposals/summaries as PDF | exporter |
| `api` | HTTP surface (FastAPI routers), request/response schemas | routes, DTOs |
| `core` | Config, logging, settings, dependency wiring | config.py, di |

Each module only talks to other modules through a narrow interface (a Python class or
function contract) — never reaches into another module's internals. This is what makes it
"industry style": swapping ChromaDB for Pinecone later, or OpenAI for Groq, touches one file.

## 3. High-level data flow

```
Public sources (website, PDFs)
        │
        ▼
  ingestion (scrape + chunk)
        │
        ▼
  embeddings (vectorize)
        │
        ▼
  vectorstore (ChromaDB)
        │
        ▼  (query time)
     rag.retriever  ───────►  llm.provider  ───────►  answer + citations
        │
        ▼
     agents.orchestrator (uses rag as a tool, plus other tools)
        │
        ├── proposal_agent  → pdf.exporter
        ├── email_agent
        └── meeting_agent
        │
        ▼
     api (FastAPI routes)
        │
        ▼
     frontend (Next.js)
```

## 4. API contract (v1)

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/ingest` | Trigger ingestion of a URL/PDF into the vector store |
| POST | `/api/v1/chat` | RAG Q&A — returns answer + source citations |
| POST | `/api/v1/proposal` | Agent generates a proposal, returns PDF download link |
| POST | `/api/v1/email` | Agent drafts a reply/cold email given context |
| POST | `/api/v1/meeting/summarize` | Agent summarizes a transcript into action items |
| GET | `/api/v1/health` | Liveness check |

## 5. Tech stack

- **Backend**: FastAPI, Pydantic v2, pydantic-settings
- **Orchestration**: LangGraph (agents), LangChain (LLM/embedding abstractions)
- **Vector DB**: ChromaDB (local, zero-infra — good for a demo)
- **LLM**: provider-agnostic — OpenAI and Groq wired, switch via `.env`
- **PDF**: `reportlab`
- **Frontend**: Next.js (App Router) + Tailwind
- **Deployment**: Docker Compose (backend + frontend as two services)

## 6. Folder structure

```
eurus-ai-copilot/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI app factory, mounts routers
│       ├── core/
│       │   ├── config.py           # env-driven settings (pydantic-settings)
│       │   └── logging.py
│       ├── api/v1/
│       │   ├── router.py           # aggregates all endpoint routers
│       │   └── endpoints/
│       │       ├── chat.py
│       │       ├── ingest.py
│       │       ├── proposal.py
│       │       ├── email.py
│       │       ├── meeting.py
│       │       └── health.py
│       ├── schemas/                # Pydantic request/response models
│       ├── services/
│       │   ├── ingestion/
│       │   ├── embeddings/
│       │   ├── vectorstore/
│       │   ├── rag/
│       │   ├── agents/
│       │   ├── llm/
│       │   └── pdf/
│       └── tests/
├── frontend/                       # Next.js app
├── docker-compose.yml
├── .env.example
└── README.md
```


