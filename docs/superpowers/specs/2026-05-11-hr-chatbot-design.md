# HR Chatbot Design Spec
**Date:** 2026-05-11  
**Project:** ABC Widgets Multilingual HR Chatbot  
**Status:** Approved

---

## Overview

A multilingual (English/Spanish) RAG-based chatbot deployed on the ABC Widgets intranet. Answers HR policy questions strictly from company-provided PDFs. Cites source document and page for every answer. Escalates unanswerable questions to a human HR contact.

---

## Architecture: Three-Container Monorepo

```
orientation-hr-chatbot/
├── docker-compose.yml
├── .env.example
├── documents/                  # HR PDFs; bind-mounted into backend at ingest time
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── ingest.py               # CLI: parse → chunk → embed → upsert to Qdrant
│   ├── main.py                 # FastAPI app (POST /chat, GET /health)
│   ├── retriever.py            # embed query → Qdrant search → return chunks
│   ├── chat.py                 # assemble prompt → Claude API → return answer+citations
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── App.jsx
    │   ├── ChatWindow.jsx
    │   ├── LanguageSelector.jsx
    │   └── CitationFootnotes.jsx
    └── nginx.conf
```

**Containers:**
- **qdrant** — Official Qdrant image. Data persists to a named Docker volume.
- **backend** — Python 3.11 + FastAPI. Also used for ingest via `docker compose run backend python ingest.py`.
- **frontend** — React (Vite) built at image build time, served by Nginx.

`ANTHROPIC_API_KEY` is injected via `.env` (gitignored). Never hardcoded. The `documents/` folder is bind-mounted into the backend container at ingest time only.

---

## Ingestion Flow

Triggered manually: `docker compose run backend python ingest.py`

1. **Parse** — `pdfplumber` processes each PDF page by page. Regular text extracted as-is. Tables detected and rendered as Markdown (pipe-delimited rows) to preserve structure for embedding.
2. **Chunk** — ~500-token chunks with 50-token overlap. Metadata attached per chunk: `source_file`, `page_number`. Tables are kept whole (not split mid-row) even if they exceed the chunk size target.
3. **Embed** — `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (768-dim, ~1GB, runs locally in Docker). Handles both English and Spanish without a translation step.
4. **Upsert** — Chunks upserted into a single Qdrant collection. The collection is **wiped and rebuilt from scratch on every ingest run**, ensuring stale content from removed PDFs never survives a re-index.
5. **Idempotent** — Running ingest twice on the same files produces the same result.

**Embedding model rationale:** `paraphrase-multilingual-mpnet-base-v2` is chosen over the smaller MiniLM variant for better cross-lingual retrieval accuracy. Since compute constraints are not a concern and the model runs locally (HR documents never leave the network), the size trade-off is acceptable.

---

## Chat Request Flow

**Endpoint:** `POST /chat`  
**Request body:** `{ message: string, language: "en" | "es", history: Message[] }`  
**Response body:** `{ answer: string, citations: [{ source_file: string, page_number: number }] }`

1. **Embed query** — User message embedded with the same multilingual model.
2. **Retrieve** — Qdrant top-5 similarity search. Returns chunks with `source_file` and `page_number`.
3. **Assemble prompt** — System prompt instructs Claude to:
   - Answer strictly from the provided context chunks
   - Respond in the language specified by `language` (English or Spanish)
   - Decline off-topic questions politely, redirect to HR topics
   - If answer not present in context: say so plainly and escalate to *"Please contact Jane Smith at hr@abcwidgets.fake or (555) 867-5309"*
   - Number sources referenced so the frontend can render footnotes
4. **LLM call** — `claude-sonnet-4-6` via Anthropic SDK. `history` passed as prior messages for multi-turn support.
5. **Return** — FastAPI returns `{ answer, citations }`.

---

## Frontend

Single-page React app (Vite), no router, no external state library.

**Components:**
- **`LanguageSelector`** — Dropdown at top of page. Options: English / Español. Defaults to English. Persists in React state for the session (ephemeral — cleared on refresh). Sent with every `/chat` request.
- **`ChatWindow`** — Scrollable message list. User messages right-aligned, assistant messages left-aligned. Conversation history in `useState` (ephemeral). Loading indicator while awaiting backend response.
- **`CitationFootnotes`** — Rendered below each assistant message when citations are present. Format: `[1] ABC_Widgets_Employee_Handbook_Full.pdf, p. 9`.
- **`App.jsx`** — Composes the above, owns history state, handles `fetch` to backend.

Backend URL injected via Vite env variable `VITE_API_URL` set in `docker-compose.yml`. No hardcoded localhost references.

---

## Testing

Tests in `backend/tests/`, run with `pytest`. No frontend tests.

| Area | Type | What's verified |
|---|---|---|
| Chunking | Unit | Table content rendered as Markdown; no mid-row splits; correct metadata attached |
| Retrieval | Integration (live Qdrant) | Known query returns chunk from expected page |
| Prompt assembly | Unit | Off-topic → refusal + escalation; language param threads correctly; no-context → escalation contact included |
| Language handling | Unit | Spanish query retrieves relevant English-document chunks (cross-lingual) |

No mocking of the Qdrant client in integration tests — uses a real instance to avoid mock/prod divergence.

---

## Implementation Phases

1. **Project skeleton** — Docker setup, environment configuration, directory structure, health check.
2. **PDF ingestion pipeline** — parse → chunk → embed → store.
3. **Backend chat API** — retrieval, prompt assembly, Claude API call, citation response.
4. **Frontend chat UI** — language selector, chat window, citation footnotes.
5. **End-to-end smoke test** — verify against the example PDF.

---

## Out of Scope

- Authentication (handled at network layer)
- Admin UI for document management
- Analytics / usage dashboards
- Real-time document updates (manual re-index is sufficient)
- Persistence of conversation history across sessions
