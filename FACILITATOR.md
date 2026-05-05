# Facilitator Guide

For whoever's running the workshop. Treat this as a one-page running order; the actual content lives in `TUTORIAL.md` and `PROMPT.md`.

If you're an attendee, you don't need to read this — start at [`README.md`](README.md).

---

## Pre-Session Checklist (Day Of)

Run through this 30 minutes before attendees arrive:

- [ ] Anthropic API keys generated and ready to hand out (one per attendee, or a shared classroom key).
- [ ] You have a working clone of the repo and have done a dry run of `Follow the instructions in @PROMPT.md.` end-to-end at least once on this machine. Mid-session is the worst time to discover a regression.
- [ ] Docker Desktop is running on your demo machine.
- [ ] The Claude Code extension is signed in and the model is set to a current Claude (Sonnet or Opus 4.x).
- [ ] You have a backup network plan (mobile hotspot) in case venue Wi-Fi goes sideways during model downloads.
- [ ] Slack/Teams channel for the session is open so you can paste the API key there for attendees.

## Opening (5 minutes)

Set the frame before anyone starts typing. The point of the session is **prompt engineering**, not "watch Claude build a chatbot." If attendees walk out remembering only the chatbot, you've under-delivered.

Suggested talking points:

1. *"The artifact you're going to walk out with isn't the chatbot — it's `PROMPT.md`. The chatbot is just a vehicle to study the prompt."*
2. *"This is exactly the kind of system a real internal team builds: multilingual, RAG, no hallucinations, citations, dockerized. It's not a toy."*
3. *"Claude is going to ask you clarifying questions, propose a plan, and then build in five reviewable phases. Your job at every checkpoint is to actually run what was built — not just say 'continue.'"*

## Set-Up Verification (5–10 minutes)

Have attendees:

1. Clone the repo and `cd` into it.
2. Open it in VS Code with the Claude Code panel.
3. Open `PROMPT.md` and `.claude/settings.json` — *look at them* for one minute. The file structure is the lesson preview.
4. Drop the API key into `.env` (or confirm Ollama is running).

**Common failure here:** the Claude Code extension isn't signed in. Easy fix; have attendees re-auth. Budget 5 minutes for stragglers.

## Phase Walkthrough (the bulk of the session)

The full attendee-facing procedure is in [`TUTORIAL.md`](TUTORIAL.md). Your job during each phase:

- **At the start of the phase**, briefly say what to expect and what they're looking for.
- **At the end of the phase**, run the verification step *with* them (or have one volunteer demo). Don't let people skip verification — that's the whole point of the staged approach.
- **Pause for questions** at each transition. The questions tell you whether the concept landed.

Rough timing on a fast cohort with the API path:

| Phase | Approx. Time | Notes |
|---|---|---|
| Clarifying Qs + plan | 5 min | Mostly Claude reading + asking |
| 1: Skeleton + Docker | 5–8 min | Mostly file writes |
| 2: Ingestion | 10–15 min | First slow phase — embedding model downloads on first build (~400MB) |
| 3: Backend API | 10 min | Lots of code; lots of teaching surface |
| 4: Frontend | 10 min | npm install dominates |
| 5: Smoke test | 10 min | Where the requirements really get tested |

Plan for ~75 minutes hands-on plus 15 minutes of opening/closing. Tighten by skipping the `npm install` wait with everyone — show on your machine while their installs run.

## Key Teaching Moments

Pause and explain when:

- **Claude asks clarifying questions.** *"Notice it didn't just start coding. The prompt told it to ask first. That's a deliberate guardrail."*
- **Claude proposes the plan.** *"Read this. If it doesn't match the prompt, push back now — it's much cheaper than fixing it after the code is written."*
- **Claude justifies a choice** (e.g., chunk size, embedding model). *"This is what we asked for: rationale in chat, not buried in comments. You can disagree with the choice now."*
- **The escalation behavior fires** during the smoke test. *"Notice the chatbot didn't make something up. That's the hallucination requirement working."*
- **The off-topic refusal fires.** *"Notice it didn't answer the trivia question. The prompt said this is a corporate HR tool, not a free LLM — and Claude carried that through to the system prompt it's using at runtime."*

## Common Attendee Questions and Good Answers

- *"Why didn't the prompt specify [some detail]?"* — Because that detail wasn't load-bearing. A good prompt names what the engineer would otherwise get wrong, not what they'd get right by default.
- *"Could I have just told Claude all this conversationally instead?"* — Yes, and people do. The reason to put it in a versioned `PROMPT.md` is so the prompt is reusable, reviewable, and inspectable. Production teams version their prompts the way they version their code.
- *"Why both Claude and Ollama?"* — Because real teams iterate locally without paying API costs and ship to production with a hosted model. Pluggable LLM providers are the norm, not the exception.
- *"Does this work for any PDFs?"* — Yes — that's what the "Inputs" section of the prompt is enforcing. Have someone drop a different PDF in and re-run the ingest step to prove it.
- *"What about authentication / admin UI / analytics?"* — Out of scope. Show them the **Out of Scope** section of the prompt. *"A good prompt also says what NOT to build."*

## When Something Goes Wrong

- **Claude proposes the wrong stack.** Don't accept it. Push back: *"The prompt requires React/FastAPI/local embeddings. Revise."* This is also a teaching moment — the prompt isn't a suggestion.
- **A bash command keeps prompting for permission.** Confirm `defaultMode: acceptEdits` is in `.claude/settings.json` and the relevant command is in the allow-list. If a new command is needed, add it live and explain.
- **Embedding model download stalls.** Use the time productively — walk through what just got written. Have attendees explain back what they see.
- **Spanish answers come back in English.** Tell Claude: *"Spanish responses aren't honoring the language selection. Show me how the language flows from the UI through to the system prompt."* This is a great debugging-with-Claude demonstration.
- **Tables come back garbled in the answers.** Tell Claude: *"Tables aren't preserved. Show me the parsing step."* Reference `pdfplumber` if it isn't already using it.
- **An attendee falls behind by two phases.** Don't try to catch them up live. Pair them with a neighbor or have them watch your screen. Catch-up time after the session if possible.

## Closing (5 minutes)

Pull it back to the prompt artifact. Suggested closing:

1. Open `PROMPT.md` on the projector.
2. Walk through the **section structure** one more time: Role, What We're Building, Inputs, Functional Requirements, Technical Constraints, Out of Scope, How I Want You to Work.
3. Highlight the four principles from the bottom of `TUTORIAL.md` ("What to Take Away"):
   - Every constraint has a `Why:`.
   - Stack choices that matter are pinned; everything else is left to Claude with a request for explanation.
   - The prompt tells Claude *how to work*, not just *what to build*.
   - Known pitfalls are pre-loaded into the prompt.
4. *"This structure works for almost any agentic build, not just chatbots. Steal it."*

## After the Session

- [ ] Revoke the temporary Anthropic API key(s).
- [ ] Send attendees a follow-up with: a link to this repo, links to relevant Claude Code docs, and your contact for follow-up questions.
- [ ] Capture lessons learned (what landed, what didn't) in this file's revision history for the next time you run the workshop.
