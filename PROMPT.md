# Build an HR Chatbot for ABC Widgets

## Role & Context

You're a senior engineer helping ABC Widgets build an internal tool for their HR department. ABC Widgets is a mid-sized U.S. manufacturer with a multilingual workforce. Their HR team is small — they spend a significant portion of every week answering walk-in questions that are already covered in the employee handbook and benefits documents. Two reasons employees walk in instead of reading the documents themselves: a meaningful share of the workforce does not read English fluently, and it is genuinely hard to find a specific answer inside a hundred-page PDF.

We're building a chatbot to absorb the repetitive questions so HR can spend its time on cases that actually need a human.

## What We're Building

A multilingual chatbot, deployed on the company's intranet, that answers HR policy questions strictly from documents the company provides. It must cite the source document and page for every answer, and respond in the language the employee selects.

## Inputs

ABC Widgets HR will provide PDF documents — handbooks, benefits guides, leave-policy materials, retirement-plan notices, and so on. The exact set will change over time as HR updates policies. The system must work for any PDFs the company drops in. One example PDF is included in this project for development; treat it as a single example, not as the full contract — your implementation should generalize.

**One pitfall to head off:** these documents lean heavily on tables — benefits matrices, eligibility charts, contribution tiers, leave-accrual schedules. Naive PDF-to-text extraction flattens tables into garbled rows that embed poorly, and the chatbot will then answer questions about benefits or eligibility confidently and wrongly. Use a PDF parser that preserves tabular structure (`pdfplumber` is one library that handles this well) and represent tables in the embedded chunks in a form a language model can actually read.

## Functional Requirements

- **Answers come only from retrieved document content.** Hallucination is the single biggest risk here — confident-sounding wrong answers about benefits eligibility, leave, or retirement matching can cause real harm. If the answer isn't present in the retrieved material, or the model isn't confident in what it found, the chatbot must say so plainly and escalate the employee to a human HR contact. If you can't derive the HR contact from the documents themselves, use a clearly-marked placeholder (e.g., "Contact HR at hr@abcwidgets.example or extension 1234") so it's obvious what needs to be filled in before deployment.
- **Stay on-topic.** The chatbot answers HR-policy questions for ABC Widgets employees, and nothing else. If a user asks about general knowledge, current events, coding help, jokes, or anything outside the provided HR documents, it politely declines and redirects them back to HR topics. *Why: this is a corporate HR tool, not a free general-purpose LLM for the workforce.*
- **Every answer cites source document and page.** *Why: HR needs to audit answers; employees need to verify them against the source.*
- **Two supported languages: English and Spanish.** *Why: a meaningful share of ABC Widgets' workforce is more comfortable in Spanish. The embedding model and the LLM both need to handle both languages well.*
- **The employee picks the response language manually.** Documents themselves may be authored in any language; retrieval should work across the language barrier where possible.
- **Multi-turn conversations.** Follow-up questions must work in context.

## Technical Constraints

- **Retrieval-augmented generation backed by a vector database.** Documents are chunked, embedded, and stored at ingest time; queries are embedded and matched against the store at runtime. *Why: grounding plus auditable citations.*
- **Pluggable LLM provider.** The system must support both the **Claude API** (for production) and **Ollama** (for local development), switchable via an environment variable with no code changes. *Why: developers iterate locally without API costs; production runs on Claude.*
- **Embedding and vector similarity run locally — no third-party embedding APIs.** The model must handle both English and Spanish. Choose accordingly and explain your choice. *Why: HR documents are sensitive and we don't want them flowing to external services at ingest time. Local embedding also keeps re-indexing free and offline-capable.*
- **Frontend built with React.** *Why: the rest of ABC Widgets' internal tooling is React, and the team wants this app to fit that stack.*
- **Backend built in Python with FastAPI.** *Why: the RAG and ML libraries the team will rely on are Python-native, and FastAPI gives us a small, well-typed HTTP layer without ceremony.*
- **Dockerized stack.** The whole thing runs with `docker compose up`. ABC Widgets' IT team will not pip-install anything on the production box.
- **Re-indexing documents must not require rebuilding containers.** HR drops new or updated PDFs into a folder, runs an ingest step, and the chatbot picks up the new content. Stale content from removed or replaced PDFs must not survive a re-index.
- **Secrets live in environment variables**, never in source control.

## Out of Scope

- Authentication — handled at the network layer; the app sits inside the intranet.
- Admin UI for managing documents.
- Analytics or usage dashboards.
- Real-time document updates — a manual re-index step is fine.

Don't build these. If you believe one is critical, raise it as a clarifying question rather than implementing it.

## How I Want You to Work

1. **Read the example PDF in the documents folder, then ask any clarifying questions** you have about the requirements before designing anything.
2. **Propose an architecture and a phased implementation plan, then wait for my approval before writing code.** Cover: overall project layout, the ingestion flow, the chat request flow, container layout, and how the LLM provider gets swapped.
3. **Implement in phases, pausing after each one** so I can review and run things:
   1. Project skeleton, Docker setup, environment configuration.
   2. PDF ingestion pipeline (parse → chunk → embed → store).
   3. Backend chat API with retrieval and LLM calls.
   4. Frontend chat UI with language selector and inline citations.
   5. End-to-end smoke test against the example PDF.
4. **Write tests for non-trivial logic** — chunking, retrieval, prompt assembly, language handling.
5. **Never install Python packages on the base system.** If you need to install anything for development, use a project-local virtual environment (`.venv/`) and activate it before invoking `pip`. Keep all build artifacts inside the project directory so it's easy to throw away and start over. *Why: this runs on developers' machines; we don't want to pollute their global Python.*
6. **Use well-maintained libraries**; don't reinvent the wheel.
7. **When you make a non-obvious decision** — a model choice, a chunk size, a similarity threshold, a chunking strategy — briefly explain *why* in chat. Don't bury the rationale in code comments.

Start by reading the example PDF in the documents folder, then ask your clarifying questions.
