# orientation-hr-chatbot

A hands-on workshop in **context engineering** with Claude Code. You'll use a single carefully written prompt to drive Claude through the design and implementation of a working multilingual HR chatbot for a fictional company called **ABC Widgets**.

The point of this exercise isn't the chatbot — it's the prompt. By the end, you'll have a feel for what a *good* prompt for an agentic coding tool actually looks like.

---

## What's in This Repo

| File / Folder | Purpose |
|---|---|
| [`PROMPT.md`](PROMPT.md) | The context-engineering artifact. The thing we're really teaching. |
| [`TUTORIAL.md`](TUTORIAL.md) | Step-by-step workshop procedure. Read this for the full walkthrough. |
| [`.claude/settings.json`](.claude/settings.json) | Pre-configured Claude Code permissions so the build runs hands-off. |
| [`documents/`](documents/) | Example HR PDF for the chatbot to reason over. |

That's all you start with. Claude builds the rest.

---

## Quick Start

If you're reading this five minutes before the workshop:

1. **Install prereqs** — VS Code with the Claude Code extension, the `superpowers` Claude Code plugin, Docker Desktop running, Python 3.11+, Node 18+, Git. See [`TUTORIAL.md`](TUTORIAL.md) for full details.
2. **Pick an LLM endpoint** — either an Anthropic API key (we'll provide a temporary one for the session) or local Ollama with `ollama pull llama3.2`. API key is the recommended path.
3. **Clone and open** —
   ```bash
   git clone https://github.com/ndindl/orientation-hr-chatbot.git
   cd orientation-hr-chatbot
   code .
   ```
4. **Open the Claude Code panel** in VS Code.
5. **In the chat input, type:**
   > Follow the instructions in @PROMPT.md.

   That's it. Claude will ask clarifying questions, propose a plan, and then build the app in five reviewable phases.
6. **Press `Shift+Tab`** to switch to acceptEdits mode so file writes don't prompt.

For everything else — what to expect at each phase, how to verify the requirements, and what to do when things go wrong — see [`TUTORIAL.md`](TUTORIAL.md).

---

## Workshop Outcomes

You'll leave with:

- A running, dockerized HR chatbot built end-to-end by Claude under your supervision.
- A reusable `PROMPT.md` you can adapt to your own projects.
- A working `.claude/settings.json` you can lift into other repos to cut down on approval prompts.
- A clearer mental model of how to *talk to* Claude Code: name the problem and the non-negotiables, leave the rest to the agent, and define checkpoints so you stay in the loop.

---

## A Note on the API Key

If you're using the workshop's temporary Anthropic API key:

- Treat it like any production secret — don't commit it, don't share it.
- It will be revoked a few days after the session.
- Put it in `.env` (which the generated `.gitignore` will exclude), never directly in source.

If you want to keep working on the project after the workshop, [generate your own Anthropic API key](https://console.anthropic.com/) and swap it in.

---

## License

Educational use. Documents in `documents/` are fictional or anonymized example HR materials and are not real company policy.
