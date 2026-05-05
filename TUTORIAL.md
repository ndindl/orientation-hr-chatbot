# Workshop: Building an HR Chatbot with Claude Code

A hands-on tutorial in **context engineering** — using a single well-crafted prompt to drive Claude Code through the design and implementation of a real, working application.

By the end of this session, you'll have a multilingual, RAG-based HR chatbot running locally on your machine — and, more importantly, a feel for what a *good* prompt for an agentic coding tool looks like.

---

## What You'll Build

An internal-style HR chatbot for a fake company called **ABC Widgets**. Specifically:

- A **React** chat UI with a language selector (English / Spanish).
- A **Python / FastAPI** backend that does retrieval-augmented generation against PDF HR documents.
- A **local vector database** populated by an ingestion script that parses, chunks, and embeds the PDFs.
- A **pluggable LLM layer** that runs against the **Claude API** (production) or **Ollama** (local dev) with a single env var change.
- The whole thing **dockerized**, so `docker compose up` is the only command anyone needs to run.

The chatbot will answer questions strictly from the documents you give it, cite the source document and page in every answer, escalate to a human HR contact when it doesn't know, and politely refuse to be turned into a free general-purpose chatbot.

## What You'll Be Given

The tutorial repo contains three things:

| File / folder | What it is |
|---|---|
| `PROMPT.md` | The context-engineering artifact. The thing we're really teaching. |
| `.claude/settings.json` | A pre-configured Claude Code permissions file so the build runs mostly hands-off. |
| `documents/` | Contains an example HR PDF for the chatbot to reason over. |

That is intentionally minimal. Claude builds everything else.

---

## Project Requirements (What the Prompt Encodes)

These are the requirements the prompt is asking Claude to satisfy. As the build proceeds, you'll see Claude's choices map back to each one.

**Functional**

1. Answers come *only* from retrieved document content. Hallucination is the top risk.
2. If the answer isn't in the docs, escalate to a human HR contact (with a clearly-marked placeholder).
3. Stay on-topic — refuse off-topic questions; don't be a general-purpose LLM.
4. Cite source document + page on every answer.
5. Two languages: English and Spanish. The user picks.
6. Multi-turn conversation (follow-ups work).

**Technical**

1. RAG, backed by a vector database.
2. Pluggable LLM provider — Claude API for production, Ollama for local dev, env-var switchable.
3. Local embedding model — no third-party embedding APIs.
4. PDF parser must preserve table structure (a known pitfall — naive extraction garbles benefits matrices).
5. React frontend, Python/FastAPI backend.
6. Dockerized — runs with `docker compose up`.
7. Re-indexing doesn't require rebuilding containers.

Take a few minutes to skim `PROMPT.md` itself before you start. The structure (Role, What We're Building, Inputs, Functional Requirements, Technical Constraints, Out of Scope, How I Want You to Work) is itself the lesson.

---

## Prerequisites

Have these installed and working **before** the session starts:

| Requirement | Notes |
|---|---|
| **VS Code** | With the **Claude Code** extension installed and authenticated. |
| **Docker Desktop** | Running. Verify with `docker info`. |
| **Python 3.11+** | For local development. `python3 --version`. |
| **Node.js 18+** | For the React frontend tooling. `node --version`. |
| **Git** | For cloning the tutorial repo. |
| **An LLM endpoint** | Either an **Anthropic API key** *or* **Ollama** running locally with a model pulled. See below. |

### Choosing your LLM endpoint

You have two options. Pick one — you can switch later by editing `.env`.

**Option A — Anthropic API key (recommended for the workshop).** Simpler, faster. We'll provide a temporary API key during the session that will be revoked afterward. Treat it like a production secret while you have it: don't commit it, don't share it.

**Option B — Local Ollama.** No API key, no cost, no internet round-trip — but requires installing Ollama and pulling a model to disk. If you choose this:

```bash
# Install Ollama from https://ollama.ai, then:
ollama pull llama3.2     # ~2GB; small but capable enough for the tutorial
ollama serve             # runs the local API on port 11434
```

Larger models (`llama3.1:8b`, `mistral`, etc.) will give better Spanish answers but take much longer to download. `llama3.2` is the lowest-friction choice for the workshop.

After Phase 1 of the build (when Claude generates `.env.example`), check that `LLM_MODEL` matches the model you pulled. If Claude picked a different default, edit your `.env` to point at `llama3.2` — Ollama will only serve models it has on disk.

If you're unsure between A and B, pick A.

---

## Setup

1. **Clone the tutorial repo.**
   ```bash
   git clone https://github.com/ndindl/orientation-hr-chatbot.git
   cd orientation-hr-chatbot
   ```

2. **Open it in VS Code.**
   ```bash
   code .
   ```

3. **Inspect what you have.** Open `PROMPT.md` and `.claude/settings.json`. Glance at the PDF in `documents/`.

4. **Open the Claude Code panel** (sidebar in VS Code, or `Cmd/Ctrl+Shift+P` → "Claude Code").

---

## Running the Build

1. In the Claude Code chat input, type exactly:

   > Follow the instructions in @PROMPT.md.

   The `@` is important — it tells Claude Code to load the file as context.

2. Claude will respond with **clarifying questions** (the prompt asks it to). Answer them concisely. Some likely ones:
   - *Where should the chatbot's HR contact placeholder default to?* → "Use `hr@abcwidgets.example` and extension 1234."
   - *Should the language selector default to English?* → "Yes."
   - *Anything else specific to ABC Widgets I should know?* → "No, treat it as a generic mid-sized U.S. manufacturer."

3. Claude will then propose an **architecture and a phased plan**. Read it. Push back if anything looks wrong. When you're satisfied, tell it to proceed.

4. Press `Shift+Tab` once to switch into **acceptEdits** mode. (The committed `settings.json` already does most of this for you, but acceptEdits ensures Claude can write files without each one prompting you.)

5. Claude implements in **five phases**, pausing after each one for your review. See the next section.

---

## The Five Build Phases

Claude will pause at the end of each phase. Use those pauses to *actually run* what was just built — don't just nod and say "continue." The point of a checkpoint is to catch problems early.

### Phase 1 — Project skeleton, Docker, env config

**You'll get:** a directory layout, a `docker-compose.yml`, a `Dockerfile` per service, a `.env.example`, and stub source files.

**Verify:** `docker compose config` parses without error. `.env.example` lists `LLM_PROVIDER`, an API key var, embedding model, vector DB host, etc.

### Phase 2 — PDF ingestion pipeline

**You'll get:** a script (often `ingest.py`) that parses PDFs in `documents/`, chunks them, embeds them, and stores them in the vector DB. The vector DB container should start cleanly.

**Verify:** run the ingest script. Confirm it processed the example PDF, including any tables. Ask Claude to show you a sample chunk so you can eyeball the table preservation.

### Phase 3 — Backend chat API with retrieval and LLM calls

**You'll get:** FastAPI endpoints (typically `POST /api/chat`), a retrieval module, prompt assembly, and the pluggable LLM adapter.

**Verify:** `curl` the chat endpoint with an English question whose answer is in the example PDF. You should get a grounded answer with a citation. Try a question whose answer *isn't* in the doc — you should get an escalation to the placeholder HR contact, not a confident-sounding fabrication.

### Phase 4 — Frontend chat UI

**You'll get:** a React app with a chat window, language selector, message bubbles, and citation display.

**Verify:** open the frontend in your browser. Send a question. Check that citations render. Switch the selector to Spanish and ask the same question — you should get a Spanish answer.

### Phase 5 — End-to-end smoke test

**You'll get:** a documented happy-path run, possibly an automated test or a README section.

**Verify the requirements end-to-end:**

| Test | Expected behavior |
|---|---|
| Ask a question with an answer in the doc | Grounded answer + citation |
| Ask a question whose answer isn't in the doc | "I don't know — please contact HR…" |
| Ask "What's the capital of France?" | Polite refusal, redirect to HR topics |
| Ask the same question in Spanish | Spanish answer, still cited |
| Ask a follow-up that depends on prior context | Coherent answer that uses the previous turn |
| Replace the example PDF, re-run ingest | New content reflected; old content gone |

If any of these fail, that's a real bug — tell Claude what failed and ask it to fix.

---

## When Things Go Wrong

A few common failure modes and how to handle them:

- **Claude proposes a stack that doesn't match the prompt.** Push back: "The prompt requires React/FastAPI/local embeddings. Revise the plan." Don't let it drift.
- **Approval prompts every few seconds.** Confirm you're in `acceptEdits` mode (Shift+Tab) and that `.claude/settings.json` is committed at the project root.
- **The model downloads take forever.** Expected on first run — the multilingual sentence-transformers model is ~400MB; Ollama models can be several GB. Use this time to read what Claude wrote.
- **The chatbot answers off-topic questions anyway.** Tell Claude: "The on-topic constraint isn't being enforced. Show me the system prompt and tighten it."
- **Tables come back garbled.** Tell Claude: "Tables aren't preserved. Show me the parsing step and fix it." Reference `pdfplumber` if it isn't already using it.
- **Spanish answers come back in English.** Tell Claude: "Spanish responses aren't honoring the language selection. Show me how the language flows from the UI through the system prompt."

In all cases, lean on Claude — it built it, it can fix it. Be specific about what's failing.

---

## What to Take Away

When you walk out of the session, the artifact that matters isn't the running chatbot — it's `PROMPT.md`. Re-read it once at the end and notice:

1. **Every constraint has a `Why:`.** Constraints without rationale tend to get ignored or worked around. Rationale tells the model (and your future self) what's load-bearing.
2. **The prompt names the problem AND the non-negotiables, but not every implementation detail.** Stack choices that *had* to be specified (Claude/Ollama, React, FastAPI, local embeddings) are pinned. Things that didn't (specific embedding model, chunk size, vector DB choice, port numbers) are left to Claude with a request for explanation.
3. **The prompt explicitly tells Claude how to work**, not just what to build — clarifying questions first, plan before code, phased implementation, rationale in chat. That structure is what makes the build reviewable instead of a 30-minute black box.
4. **The prompt names known pitfalls** (the table extraction one). A good context engineer pre-loads the failure modes they've seen before.

You can take this prompt structure to any other Claude Code project and adapt it — that's the real deliverable.
