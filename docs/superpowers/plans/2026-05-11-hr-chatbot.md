# HR Chatbot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dockerized multilingual (English/Spanish) RAG chatbot that answers ABC Widgets HR policy questions from company PDFs, cites sources on every answer, and refuses off-topic questions.

**Architecture:** Three Docker containers: `qdrant` (vector DB, named volume), `backend` (FastAPI + RAG pipeline), `frontend` (React/Vite built by Nginx). HR PDFs are ingested via a manual CLI script (`ingest.py`) that wipes and rebuilds the Qdrant collection on every run. The backend embeds queries locally with `paraphrase-multilingual-mpnet-base-v2`, retrieves top-5 chunks, and calls `claude-sonnet-4-6` for generation.

**Tech Stack:** Python 3.11, FastAPI, pdfplumber, sentence-transformers, qdrant-client, anthropic SDK, pytest; React 18, Vite, Nginx; Docker Compose.

**Important:** Do NOT run git commands, create commits, or modify `.gitignore`. Do NOT install Python packages on the base system — use `backend/.venv/` for local development.

---

## File Map

```
docker-compose.yml
.env.example
backend/
  Dockerfile
  requirements.txt
  main.py
  pdf_parser.py        # NOTE: named pdf_parser, not parser (parser is a stdlib name)
  chunker.py
  embedder.py
  retriever.py
  chat.py
  ingest.py
  tests/
    __init__.py
    conftest.py
    test_chunker.py
    test_chat.py
    test_main.py
    test_retriever_integration.py
frontend/
  Dockerfile
  nginx.conf
  package.json
  vite.config.js
  index.html
  src/
    main.jsx
    App.jsx
    ChatWindow.jsx
    LanguageSelector.jsx
    CitationFootnotes.jsx
```

---

## Phase 1: Project Skeleton & Docker Setup

### Task 1: Root-level scaffold

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1: Create `.env.example`**

```
ANTHROPIC_API_KEY=your_key_here
```

- [ ] **Step 2: Create `docker-compose.yml`**

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.9.4
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"

  backend:
    build: ./backend
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - QDRANT_URL=http://qdrant:6333
      - DOCUMENTS_DIR=/documents
    volumes:
      - ./documents:/documents:ro
    ports:
      - "8000:8000"
    depends_on:
      - qdrant

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_URL=http://localhost:8000
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  qdrant_data:
```

---

### Task 2: Backend Dockerfile + requirements.txt

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`

- [ ] **Step 1: Create `backend/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pdfplumber==0.11.0
sentence-transformers==3.0.1
qdrant-client==1.9.1
anthropic==0.40.0
pytest==8.2.2
httpx==0.27.0
```

- [ ] **Step 2: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the multilingual embedding model at build time
# so ingest and queries don't download it at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### Task 3: Backend FastAPI skeleton with /health (TDD)

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_main.py`
- Create: `backend/main.py`

- [ ] **Step 1: Create `backend/tests/__init__.py`** (empty file)

- [ ] **Step 2: Write the failing test — create `backend/tests/test_main.py`**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Run test to verify it fails**

First, set up the local venv (used for all local pytest runs throughout this plan):
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run:
```bash
python -m pytest tests/test_main.py -v
```
Expected: `ModuleNotFoundError` — `main.py` doesn't exist yet.

- [ ] **Step 4: Create `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ABC Widgets HR Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run test to verify it passes**

```bash
python -m pytest tests/test_main.py -v
```
Expected: `test_health_returns_ok PASSED`

---

### Task 4: Frontend scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx` (placeholder — replaced in Task 18)

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "hr-chatbot",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.8"
  }
}
```

- [ ] **Step 2: Create `frontend/vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

- [ ] **Step 3: Create `frontend/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ABC Widgets HR Assistant</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Create `frontend/src/main.jsx`**

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 5: Create `frontend/src/App.jsx` (placeholder)**

```jsx
export default function App() {
  return <div><h1>ABC Widgets HR Assistant</h1><p>Coming soon...</p></div>
}
```

---

### Task 5: Frontend Dockerfile + nginx.conf

**Files:**
- Create: `frontend/nginx.conf`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Create `frontend/nginx.conf`**

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 2: Create `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

### Task 6: Verify docker compose up

**Prerequisite:** Docker Desktop is running.

- [ ] **Step 1: Copy .env.example to .env and add a placeholder key**

```bash
cp .env.example .env
```
Open `.env` and set `ANTHROPIC_API_KEY=placeholder` for now (we don't call it in this phase).

- [ ] **Step 2: Build all images**

```bash
docker compose build
```
Expected: All three images build without errors. The backend build downloads the ~1GB embedding model — takes ~5 minutes on first run.

- [ ] **Step 3: Start all containers**

```bash
docker compose up -d
```
Expected: `qdrant`, `backend`, and `frontend` containers all show `Started`.

- [ ] **Step 4: Verify backend health**

```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

- [ ] **Step 5: Verify frontend loads**

Open `http://localhost:3000`. Expected: page shows "ABC Widgets HR Assistant / Coming soon..."

- [ ] **Step 6: Stop containers**

```bash
docker compose down
```

---

## Phase 2: PDF Ingestion Pipeline

### Task 7: pdf_parser.py

**Note:** This file is named `pdf_parser.py`, not `parser.py` — `parser` is a Python stdlib module name and must not be shadowed.

**Files:**
- Create: `backend/pdf_parser.py`

- [ ] **Step 1: Create `backend/pdf_parser.py`**

```python
import os
import pdfplumber
from dataclasses import dataclass
from typing import Generator


@dataclass
class PageContent:
    source_file: str
    page_number: int  # 1-indexed
    text: str


def parse_pdf(pdf_path: str) -> Generator[PageContent, None, None]:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = _extract_page_text(page)
            if text.strip():
                yield PageContent(
                    source_file=os.path.basename(pdf_path),
                    page_number=i + 1,
                    text=text,
                )


def _extract_page_text(page) -> str:
    tables = page.find_tables()
    table_bboxes = [t.bbox for t in tables]

    # Extract text from regions outside table bounding boxes
    filtered = page
    for bbox in table_bboxes:
        filtered = filtered.outside_bbox(bbox)
    non_table_text = (filtered.extract_text() or "").strip()

    # Render each table as Markdown so it survives embedding intact
    table_parts = []
    for table in tables:
        data = table.extract()
        if data:
            table_parts.append(_table_to_markdown(data))

    parts = []
    if non_table_text:
        parts.append(non_table_text)
    parts.extend(table_parts)
    return "\n\n".join(parts)


def _table_to_markdown(table: list[list]) -> str:
    rows = []
    for i, row in enumerate(table):
        cells = [str(cell or "").replace("\n", " ").strip() for cell in row]
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            rows.append("| " + " | ".join(["---"] * len(row)) + " |")
    return "\n".join(rows)
```

- [ ] **Step 2: Smoke-test the parser against the example PDF**

```bash
cd backend
source .venv/bin/activate
python -c "
from pdf_parser import parse_pdf
pages = list(parse_pdf('../documents/ABC_Widgets_Employee_Handbook_Full.pdf'))
print(f'Pages parsed: {len(pages)}')
for p in pages:
    if '|' in p.text:
        print(f'Table found on page {p.page_number}:')
        print(p.text[:400])
        break
"
```
Expected: 27 pages parsed. At least one page printed contains `|` pipe characters in Markdown table format (not garbled text).

---

### Task 8: chunker.py (TDD)

**Files:**
- Create: `backend/tests/test_chunker.py`
- Create: `backend/chunker.py`

- [ ] **Step 1: Write the failing tests — create `backend/tests/test_chunker.py`**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pdf_parser import PageContent
from chunker import chunk_page, _has_table


def _make_page(text, page_number=1, source="test.pdf"):
    return PageContent(source_file=source, page_number=page_number, text=text)


def test_short_text_returns_single_chunk():
    chunks = chunk_page(_make_page("Short vacation policy text."))
    assert len(chunks) == 1
    assert chunks[0].text == "Short vacation policy text."


def test_chunk_carries_source_metadata():
    chunks = chunk_page(_make_page("Some text.", page_number=5, source="handbook.pdf"))
    assert chunks[0].source_file == "handbook.pdf"
    assert chunks[0].page_number == 5


def test_long_text_splits_into_multiple_chunks():
    page = _make_page(" ".join(["word"] * 600))
    chunks = chunk_page(page, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_overlap_connects_adjacent_chunks():
    words = [str(i) for i in range(600)]
    chunks = chunk_page(_make_page(" ".join(words)), chunk_size=500, overlap=50)
    last_word_of_chunk0 = chunks[0].text.split()[-1]
    assert last_word_of_chunk0 in chunks[1].text.split()


def test_page_with_table_is_not_split():
    table_text = (
        "Policy overview.\n\n"
        "| Years of Service | Hours Biweekly | Max Days |\n"
        "| --- | --- | --- |\n"
        "| 0-5 | 3.077 | 10 |\n"
        "| 6-10 | 4.62 | 15 |"
    )
    chunks = chunk_page(_make_page(table_text))
    assert len(chunks) == 1
    assert "| 0-5 |" in chunks[0].text
    assert "| 6-10 |" in chunks[0].text


def test_has_table_detects_pipe_lines():
    assert _has_table("| a | b |\n| --- | --- |") is True
    assert _has_table("Regular text without pipes.") is False


def test_all_chunks_have_incrementing_index():
    page = _make_page(" ".join(["word"] * 600))
    chunks = chunk_page(page, chunk_size=500, overlap=50)
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && source .venv/bin/activate
python -m pytest tests/test_chunker.py -v
```
Expected: `ModuleNotFoundError: No module named 'chunker'`

- [ ] **Step 3: Create `backend/chunker.py`**

```python
from dataclasses import dataclass
from pdf_parser import PageContent


@dataclass
class Chunk:
    source_file: str
    page_number: int
    text: str
    chunk_index: int


def _has_table(text: str) -> bool:
    return any(line.strip().startswith("|") for line in text.splitlines())


def chunk_page(page: PageContent, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    # Keep table-containing pages as a single chunk to prevent mid-row splits
    if _has_table(page.text):
        return [Chunk(
            source_file=page.source_file,
            page_number=page.page_number,
            text=page.text,
            chunk_index=0,
        )]

    words = page.text.split()
    if len(words) <= chunk_size:
        return [Chunk(
            source_file=page.source_file,
            page_number=page.page_number,
            text=page.text,
            chunk_index=0,
        )]

    chunks = []
    start = 0
    idx = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(Chunk(
            source_file=page.source_file,
            page_number=page.page_number,
            text=" ".join(words[start:end]),
            chunk_index=idx,
        ))
        if end == len(words):
            break
        start = end - overlap
        idx += 1
    return chunks
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_chunker.py -v
```
Expected: All 7 tests `PASSED`

---

### Task 9: embedder.py

**Files:**
- Create: `backend/embedder.py`

- [ ] **Step 1: Create `backend/embedder.py`**

```python
from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    vectors = _get_model().encode(texts, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    return embed([text])[0]
```

- [ ] **Step 2: Smoke-test the embedder**

```bash
cd backend && source .venv/bin/activate
python -c "
from embedder import embed_query
v = embed_query('How many vacation days do I get?')
print(f'Vector length: {len(v)}, first 3 values: {v[:3]}')
"
```
Expected: `Vector length: 768, first 3 values: [<float>, <float>, <float>]`

Note: First run downloads ~1GB model to `~/.cache/huggingface/`. Subsequent runs are instant.

---

### Task 10: ingest.py

**Files:**
- Create: `backend/ingest.py`

- [ ] **Step 1: Create `backend/ingest.py`**

```python
import os
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from pdf_parser import parse_pdf
from chunker import chunk_page
from embedder import embed

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "hr_documents"
VECTOR_SIZE = 768
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "./documents")


def main():
    client = QdrantClient(url=QDRANT_URL)

    # Wipe and rebuild on every run — this ensures stale content from
    # removed or replaced PDFs never survives a re-index
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection '{COLLECTION_NAME}'")

    pdf_files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {DOCUMENTS_DIR}")
        return

    all_chunks = []
    for pdf_path in sorted(pdf_files):
        print(f"Parsing {pdf_path} ...")
        for page in parse_pdf(pdf_path):
            all_chunks.extend(chunk_page(page))

    print(f"Embedding {len(all_chunks)} chunks ...")
    vectors = embed([c.text for c in all_chunks])

    points = [
        PointStruct(
            id=i,
            vector=vectors[i],
            payload={
                "source_file": all_chunks[i].source_file,
                "page_number": all_chunks[i].page_number,
                "text": all_chunks[i].text,
            },
        )
        for i in range(len(all_chunks))
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Indexed {len(points)} chunks into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
```

---

## Phase 3: Backend Chat API

### Task 11: retriever.py + integration test

**Files:**
- Create: `backend/retriever.py`
- Create: `backend/tests/test_retriever_integration.py`

- [ ] **Step 1: Create `backend/retriever.py`**

```python
import os
from qdrant_client import QdrantClient
from embedder import embed_query

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "hr_documents"


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    client = QdrantClient(url=QDRANT_URL)
    vector = embed_query(query)
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=top_k,
        with_payload=True,
    )
    return [
        {
            "text": r.payload["text"],
            "source_file": r.payload["source_file"],
            "page_number": r.payload["page_number"],
            "score": r.score,
        }
        for r in results
    ]
```

- [ ] **Step 2: Create `backend/tests/test_retriever_integration.py`**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from embedder import embed

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
TEST_COLLECTION = "test_hr_retriever"

pytestmark = pytest.mark.skipif(
    not os.getenv("QDRANT_URL"),
    reason="QDRANT_URL not set — skipping integration tests",
)


@pytest.fixture(autouse=True)
def setup_test_collection():
    client = QdrantClient(url=QDRANT_URL)
    if client.collection_exists(TEST_COLLECTION):
        client.delete_collection(TEST_COLLECTION)
    client.create_collection(
        collection_name=TEST_COLLECTION,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    text = "Employees accrue vacation at 3.077 hours biweekly for years 0-5 of continuous service."
    vectors = embed([text])
    client.upsert(
        collection_name=TEST_COLLECTION,
        points=[PointStruct(
            id=0,
            vector=vectors[0],
            payload={"text": text, "source_file": "handbook.pdf", "page_number": 9},
        )],
    )
    yield
    client.delete_collection(TEST_COLLECTION)


def test_english_query_finds_relevant_chunk(monkeypatch):
    import retriever
    monkeypatch.setattr(retriever, "COLLECTION_NAME", TEST_COLLECTION)
    monkeypatch.setattr(retriever, "QDRANT_URL", QDRANT_URL)
    from retriever import retrieve
    results = retrieve("How much vacation do I earn?", top_k=1)
    assert len(results) == 1
    assert results[0]["page_number"] == 9
    assert results[0]["source_file"] == "handbook.pdf"


def test_spanish_query_finds_english_content(monkeypatch):
    import retriever
    monkeypatch.setattr(retriever, "COLLECTION_NAME", TEST_COLLECTION)
    monkeypatch.setattr(retriever, "QDRANT_URL", QDRANT_URL)
    from retriever import retrieve
    results = retrieve("¿Cuántos días de vacaciones tengo?", top_k=1)
    assert len(results) == 1
    assert results[0]["page_number"] == 9
```

- [ ] **Step 3: Run integration tests (requires Qdrant running)**

Start Qdrant locally:
```bash
docker run -d -p 6333:6333 --name qdrant-test qdrant/qdrant:v1.9.4
```
Then run:
```bash
cd backend && source .venv/bin/activate
QDRANT_URL=http://localhost:6333 python -m pytest tests/test_retriever_integration.py -v
```
Expected: Both tests `PASSED`. The Spanish-query test confirms cross-lingual retrieval works.

Tear down the test container afterward:
```bash
docker rm -f qdrant-test
```

---

### Task 12: chat.py (TDD)

**Files:**
- Create: `backend/tests/test_chat.py`
- Create: `backend/chat.py`

- [ ] **Step 1: Write the failing tests — create `backend/tests/test_chat.py`**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock
from chat import build_system_prompt, chat

SAMPLE_CHUNKS = [
    {
        "text": "Vacation accrual is 3.077 hours biweekly for years 0-5.",
        "source_file": "handbook.pdf",
        "page_number": 9,
        "score": 0.92,
    }
]


def test_system_prompt_specifies_english():
    assert "English" in build_system_prompt(SAMPLE_CHUNKS, "en")


def test_system_prompt_specifies_spanish():
    assert "Spanish" in build_system_prompt(SAMPLE_CHUNKS, "es")


def test_system_prompt_includes_hr_contact():
    prompt = build_system_prompt(SAMPLE_CHUNKS, "en")
    assert "hr@abcwidgets.fake" in prompt
    assert "555" in prompt


def test_system_prompt_includes_chunk_text():
    assert "3.077 hours biweekly" in build_system_prompt(SAMPLE_CHUNKS, "en")


def test_system_prompt_includes_source_citation():
    prompt = build_system_prompt(SAMPLE_CHUNKS, "en")
    assert "handbook.pdf" in prompt
    assert "p.9" in prompt


def test_system_prompt_with_no_chunks_still_has_contact():
    assert "hr@abcwidgets.fake" in build_system_prompt([], "en")


def test_chat_returns_model_text(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="You earn 3.077 hours biweekly.")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_resp
    monkeypatch.setattr("chat.client", mock_client)

    result = chat("How much vacation do I earn?", SAMPLE_CHUNKS, "en", [])
    assert result == "You earn 3.077 hours biweekly."


def test_chat_passes_full_history_to_api(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="Answer.")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_resp
    monkeypatch.setattr("chat.client", mock_client)

    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello"},
    ]
    chat("Follow-up question", SAMPLE_CHUNKS, "en", history)

    messages = mock_client.messages.create.call_args[1]["messages"]
    assert len(messages) == 3  # 2 history + 1 current
    assert messages[-1]["content"] == "Follow-up question"


def test_chat_uses_correct_model(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="Answer.")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_resp
    monkeypatch.setattr("chat.client", mock_client)

    chat("Question", SAMPLE_CHUNKS, "en", [])
    assert mock_client.messages.create.call_args[1]["model"] == "claude-sonnet-4-6"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && source .venv/bin/activate
python -m pytest tests/test_chat.py -v
```
Expected: `ModuleNotFoundError: No module named 'chat'`

- [ ] **Step 3: Create `backend/chat.py`**

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_HR_CONTACT = "Jane Smith at hr@abcwidgets.fake or (555) 867-5309"

_SYSTEM_TEMPLATE = """\
You are an HR assistant for ABC Widgets. Answer employee questions strictly using the HR document excerpts provided below.

Rules:
1. Only answer questions about ABC Widgets HR policies using the provided context.
2. Respond in {language}.
3. If the question is unrelated to HR (e.g., general knowledge, coding, current events, personal advice), politely decline and redirect the employee to ask HR-related questions.
4. If the answer is not present in the context, say so plainly and direct the employee to contact {hr_contact}.
5. Reference sources using [N] notation where N matches the numbered context entries below.
6. Never fabricate information.

Context:
{context}"""


def build_system_prompt(chunks: list[dict], language: str) -> str:
    language_name = "English" if language == "en" else "Spanish"
    context_parts = [
        f"[{i}] {c['source_file']}, p.{c['page_number']}:\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    ]
    context = "\n\n".join(context_parts) if context_parts else "(No relevant context found.)"
    return _SYSTEM_TEMPLATE.format(
        language=language_name,
        hr_contact=_HR_CONTACT,
        context=context,
    )


def chat(
    message: str,
    chunks: list[dict],
    language: str,
    history: list[dict],
) -> str:
    system_prompt = build_system_prompt(chunks, language)
    messages = history + [{"role": "user", "content": message}]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_chat.py -v
```
Expected: All 8 tests `PASSED`

---

### Task 13: POST /chat endpoint

**Files:**
- Create: `backend/tests/conftest.py`
- Modify: `backend/tests/test_main.py` (append new tests)
- Modify: `backend/main.py` (add /chat endpoint)

- [ ] **Step 1: Create `backend/tests/conftest.py`**

```python
import os
import pytest

# Must be set before chat.py is imported — the Anthropic SDK raises at
# client construction time if ANTHROPIC_API_KEY is absent.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-for-pytest")


@pytest.fixture
def mock_retrieve(monkeypatch):
    chunks = [
        {
            "text": "Employees accrue 3.077 hours vacation biweekly for years 0-5.",
            "source_file": "handbook.pdf",
            "page_number": 9,
            "score": 0.92,
        }
    ]
    monkeypatch.setattr("main.retrieve", lambda q, **kwargs: chunks)
    return chunks


@pytest.fixture
def mock_chat_fn(monkeypatch):
    monkeypatch.setattr(
        "main.chat_fn",
        lambda msg, chunks, lang, hist: "You earn vacation per the accrual table.",
    )
    return "You earn vacation per the accrual table."
```

- [ ] **Step 2: Append new tests to `backend/tests/test_main.py`**

Add these after the existing `test_health_returns_ok` test:

```python
def test_chat_endpoint_returns_answer_and_citations(mock_retrieve, mock_chat_fn):
    response = client.post("/chat", json={
        "message": "How much vacation do I get?",
        "language": "en",
        "history": [],
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["citations"], list)


def test_chat_endpoint_citation_has_source_and_page(mock_retrieve, mock_chat_fn):
    response = client.post("/chat", json={
        "message": "How much vacation do I get?",
        "language": "en",
        "history": [],
    })
    citation = response.json()["citations"][0]
    assert citation["source_file"] == "handbook.pdf"
    assert citation["page_number"] == 9


def test_chat_endpoint_accepts_spanish(mock_retrieve, mock_chat_fn):
    response = client.post("/chat", json={
        "message": "¿Cuántos días de vacaciones tengo?",
        "language": "es",
        "history": [],
    })
    assert response.status_code == 200
```

- [ ] **Step 3: Run new tests to verify they fail**

```bash
python -m pytest tests/test_main.py -v
```
Expected: 3 new tests fail with 404 or import error.

- [ ] **Step 4: Replace `backend/main.py` with the full implementation**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from retriever import retrieve
from chat import chat as chat_fn

app = FastAPI(title="ABC Widgets HR Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    language: Literal["en", "es"] = "en"
    history: list[Message] = []


class Citation(BaseModel):
    source_file: str
    page_number: int


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    chunks = retrieve(req.message)
    history = [{"role": m.role, "content": m.content} for m in req.history]
    answer = chat_fn(req.message, chunks, req.language, history)
    citations = [
        Citation(source_file=c["source_file"], page_number=c["page_number"])
        for c in chunks
    ]
    return ChatResponse(answer=answer, citations=citations)
```

- [ ] **Step 5: Run all backend tests**

```bash
python -m pytest tests/test_main.py tests/test_chunker.py tests/test_chat.py -v
```
Expected: All tests `PASSED` (integration tests are skipped without `QDRANT_URL`).

---

## Phase 4: Frontend Chat UI

### Task 14: LanguageSelector.jsx

**Files:**
- Create: `frontend/src/LanguageSelector.jsx`

- [ ] **Step 1: Create `frontend/src/LanguageSelector.jsx`**

```jsx
export default function LanguageSelector({ language, onChange }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label htmlFor="lang-select" style={{ marginRight: "0.5rem", fontWeight: "bold" }}>
        Language / Idioma:
      </label>
      <select
        id="lang-select"
        value={language}
        onChange={(e) => onChange(e.target.value)}
        style={{ padding: "0.25rem 0.5rem", fontSize: "1rem" }}
      >
        <option value="en">English</option>
        <option value="es">Español</option>
      </select>
    </div>
  );
}
```

---

### Task 15: CitationFootnotes.jsx

**Files:**
- Create: `frontend/src/CitationFootnotes.jsx`

- [ ] **Step 1: Create `frontend/src/CitationFootnotes.jsx`**

```jsx
export default function CitationFootnotes({ citations }) {
  if (!citations || citations.length === 0) return null;
  return (
    <div style={{ fontSize: "0.75rem", color: "#666", marginTop: "0.4rem", textAlign: "left" }}>
      {citations.map((c, i) => (
        <div key={i}>
          [{i + 1}] {c.source_file}, p. {c.page_number}
        </div>
      ))}
    </div>
  );
}
```

---

### Task 16: ChatWindow.jsx

**Files:**
- Create: `frontend/src/ChatWindow.jsx`

- [ ] **Step 1: Create `frontend/src/ChatWindow.jsx`**

```jsx
import { useState, useRef, useEffect } from "react";
import CitationFootnotes from "./CitationFootnotes";

export default function ChatWindow({ history, loading, onSend }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div>
      <div
        style={{
          height: "500px",
          overflowY: "auto",
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "1rem",
          marginBottom: "0.75rem",
          background: "#fafafa",
        }}
      >
        {history.length === 0 && (
          <p style={{ color: "#999", textAlign: "center", marginTop: "2rem" }}>
            Ask an HR question to get started.
          </p>
        )}
        {history.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              marginBottom: "1rem",
            }}
          >
            <div style={{ maxWidth: "70%" }}>
              <div
                style={{
                  display: "inline-block",
                  background: msg.role === "user" ? "#0070f3" : "#e8e8e8",
                  color: msg.role === "user" ? "white" : "black",
                  padding: "0.6rem 1rem",
                  borderRadius: "12px",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {msg.content}
              </div>
              {msg.citations && <CitationFootnotes citations={msg.citations} />}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ color: "#999", fontStyle: "italic" }}>Thinking...</div>
        )}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask an HR question..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "0.6rem 0.8rem",
            fontSize: "1rem",
            border: "1px solid #ccc",
            borderRadius: "6px",
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            padding: "0.6rem 1.2rem",
            fontSize: "1rem",
            background: "#0070f3",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

---

### Task 17: App.jsx final wiring + frontend rebuild

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Replace the placeholder `frontend/src/App.jsx` with the full implementation**

```jsx
import { useState } from "react";
import ChatWindow from "./ChatWindow";
import LanguageSelector from "./LanguageSelector";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [language, setLanguage] = useState("en");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (message) => {
    const userMsg = { role: "user", content: message };
    const updatedHistory = [...history, userMsg];
    setHistory(updatedHistory);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          language,
          // Strip citations before sending — backend only accepts role + content
          history: history.map(({ role, content }) => ({ role, content })),
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setHistory([
        ...updatedHistory,
        { role: "assistant", content: data.answer, citations: data.citations },
      ]);
    } catch {
      setHistory([
        ...updatedHistory,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "2rem auto",
        padding: "0 1rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ marginBottom: "0.25rem" }}>ABC Widgets HR Assistant</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        Ask questions about HR policies, benefits, leave, and more.
      </p>
      <LanguageSelector language={language} onChange={setLanguage} />
      <ChatWindow history={history} loading={loading} onSend={sendMessage} />
    </div>
  );
}
```

- [ ] **Step 2: Rebuild the frontend Docker image to pick up the new components**

```bash
docker compose build frontend
```
Expected: Build completes without errors.

---

## Phase 5: End-to-End Smoke Test

### Task 18: Full build, ingest, and verify

- [ ] **Step 1: Set real ANTHROPIC_API_KEY in .env**

Open `.env` and replace the placeholder with your actual key.

- [ ] **Step 2: Rebuild all images and start containers**

```bash
docker compose build
docker compose up -d
```
Expected: All three containers start. Check for errors:
```bash
docker compose logs backend
```

- [ ] **Step 3: Run ingest**

```bash
docker compose run backend python ingest.py
```
Expected output:
```
Created collection 'hr_documents'
Parsing /documents/ABC_Widgets_Employee_Handbook_Full.pdf ...
Embedding N chunks ...
Indexed N chunks into 'hr_documents'.
```
N will be between 30–80 chunks depending on page lengths.

- [ ] **Step 4: Verify health endpoint**

```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

- [ ] **Step 5: Test English query via curl**

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many vacation days do I get after 5 years?", "language": "en", "history": []}' \
  | python3 -m json.tool
```
Expected: `answer` mentions accrual rates (3.077 hours biweekly). `citations` contains `{"source_file": "ABC_Widgets_Employee_Handbook_Full.pdf", "page_number": 9}`.

- [ ] **Step 6: Test Spanish query via curl**

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos días de vacaciones tengo?", "language": "es", "history": []}' \
  | python3 -m json.tool
```
Expected: `answer` is in Spanish. `citations` still reference the English-language PDF.

- [ ] **Step 7: Test off-topic refusal via curl**

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write me a Python function to sort a list.", "language": "en", "history": []}' \
  | python3 -m json.tool
```
Expected: `answer` politely declines and redirects to HR questions. `citations` is empty or minimal.

- [ ] **Step 8: Verify frontend in browser**

Open `http://localhost:3000`. Verify:
1. Language dropdown shows "English" by default
2. Typing a question and pressing Send shows the user message right-aligned
3. Assistant response appears left-aligned with numbered citation footnotes below it (format: `[1] ABC_Widgets_Employee_Handbook_Full.pdf, p. 9`)
4. Switching to "Español" and asking "¿Cuántos días de vacaciones tengo?" returns a Spanish-language response

- [ ] **Step 9: Test multi-turn follow-up in browser**

Ask: "What is the vacation accrual rate for new employees?"
Then follow up: "What about after 6 years?"

Expected: The second answer references the 6–10 year tier (4.62 hours biweekly), confirming multi-turn context is carried correctly.
