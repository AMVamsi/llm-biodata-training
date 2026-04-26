# AGENTS.md — LLM Biodata Training: Contributor Guide and Project Guardrails

---

## ⚡ AI AGENT QUICK BRIEF — Read this section only. Stop here unless you need specifics.

> This section is optimised for AI agents. Humans: read the full document below.

### What is already implemented — do not rebuild

| Function | File | Notes |
|----------|------|-------|
| `load_chat_model()` | `app.py:12` | Mistral + Groq; raises ValueError for unknown provider |
| `index_endpoints()` | `app.py:62` | UniProt, Bgee, OMA; deletes + recreates collection |
| `retrieve_docs()` | `app.py:101` | Top-3 per doc_type; two types filtered |
| `format_doc()` | `app.py:133` | Pure function; most testable; start tests here |
| `execute_query()` | `app.py:174` | Extracts SPARQL from markdown; calls live endpoint |
| Retry loop | `app.py:189` | Max 3 attempts; corrective feedback injection |
| `on_message()` | `app.py:343` | Chainlit handler; streaming responses |
| `set_starters()` | `app.py:378` | One starter question |

### What is planned — do not build unless explicitly asked

`ruff config`, `mypy config`, `pytest + tests/`, `Python CI workflow`, `demos/` folder reorganisation,
`project/README.md`, customised `chainlit.md`, branch protection

### Locked — do not change without explicit instruction

| File / Symbol | Reason |
|---------------|--------|
| `SYSTEM_PROMPT` in `app.py` | Controls LLM output format; breaking it breaks SPARQL extraction |
| `project/data/vectordb/` | Runtime data; recreated by `index_endpoints()` |
| `project/uv.lock` | Auto-generated; never hand-edit |
| `.github/workflows/deploy.yml` | Slides CI; unrelated to chatbot |

### Known bugs to fix (when task asks for it)

- `execute_query()` return type annotated as `list[dict]` — should be `list[dict] | None`
- `project/__pycache__/app.cpython-312.pyc` tracked in git — needs `git rm --cached`
- `project/data/vectordb/.lock` tracked in git — needs `git rm --cached`
- ~200 lines of dead commented-out code in `app.py` lines 150–340
- `langchain-ollama` declared in `pyproject.toml` but never used in code

### Before every change

```bash
git branch --show-current        # confirm branch
git diff main --name-only        # confirm what's changed
```

Check `docs/FEATURE_STATUS.md` before assuming something is missing.

### End of session: always report

Scope completed · Files changed · Tests added · Verification run · Follow-up items

---
> **For full context:** read Sections 2–11 below. For implementation contracts see Section 4.
> For scope guardrails see Section 5. For coding rules see Section 6.
---

## 📖 HUMAN CONTRIBUTOR GUIDE — Full reference below

> **Read this file first before making any change.**
> This document is the project memory for both human contributors and AI coding agents.
> Its purpose is to prevent loss of context, duplicate implementations, unauthorised refactors,
> and changes that break the application's functionality.

---

## 1. Project Summary

### 1.1 Project Name
`llm-biodata-training` (deployed as `tutorial-biodata-agent`)

### 1.2 Project Purpose
This repository contains two distinct components maintained together:

1. **Training slides** — A Vite/Reveal.js slide deck for the SIB Swiss training course
   *"Using Large Language Models for Biodata Exploration"* (`MSLS_V5_15`).
2. **SPARQL Query Assistant chatbot** — A Python RAG (Retrieval-Augmented Generation)
   application that helps researchers write SPARQL queries against biological databases through
   a natural language interface.

This document primarily governs the **chatbot application** located in `project/`.

### 1.3 Core Application Objective
Allow a user to ask natural language questions such as:
> *"What are the rat orthologs of human TP53?"*

The system will:
1. Retrieve semantically relevant SPARQL example queries and schema descriptions from a local
   vector database.
2. Pass the retrieved context to an LLM to generate a SPARQL query.
3. Execute the generated query against the appropriate live biological endpoint.
4. Validate results; retry with corrective feedback if the query returns no results (max 3 tries).
5. Summarise the final results to the user via a Chainlit chat interface.

### 1.4 Biological Endpoints Currently Indexed
| Endpoint | Description |
|----------|-------------|
| UniProt (`sparql.uniprot.org`) | Protein sequences, functions, annotations |
| Bgee (`bgee.org/sparql`) | Gene expression across tissues and species |
| OMA Browser (`sparql.omabrowser.org`) | Orthologous gene relationships |

### 1.5 Repository Layout
```text
llm-biodata-training/
├── project/                    # ← Python chatbot application (primary scope)
│   ├── app.py                  # Main application entrypoint
│   ├── pyproject.toml          # Python project metadata and dependencies
│   ├── .env.example            # Template for required API keys
│   ├── data/vectordb/          # Local Qdrant vector database (indexed at runtime)
│   ├── .chainlit/              # Chainlit UI config and translations
│   └── demos/                  # [planned] Educational demo scripts (to be moved here)
├── public/                     # Slide assets
├── .github/workflows/          # GitHub Actions (slides deploy + Python CI)
├── AGENTS.md                   # ← this file
├── CONTRIBUTING.md             # How to contribute
├── CHANGELOG.md                # History of meaningful changes
├── docs/
│   ├── FEATURE_STATUS.md       # Single source of truth for feature implementation status
│   └── architecture.md         # Detailed architecture and data flow
└── README.md                   # High-level project overview
```

---

## 2. Current Project Status

This section prevents agents from re-implementing already-completed work.
**Update it every time a major task is completed.**

| Area | Status | Notes |
|------|--------|-------|
| LLM provider setup (`load_chat_model`) | `implemented` | Mistral AI + Groq, provider/model string split pattern |
| Vector DB setup (Qdrant + FastEmbed) | `implemented` | Local Qdrant, BAAI/bge-small-en-v1.5, 384-dim cosine |
| Endpoint indexing (`index_endpoints`) | `implemented` | UniProt, Bgee, OMA; uses `sparql-llm` loaders |
| Document retrieval (`retrieve_docs`) | `implemented` | Filtered by `doc_type`: query examples + schema shapes |
| Document formatting (`format_doc`) | `implemented` | Returns markdown codeblock with endpoint comment |
| SPARQL execution (`execute_query`) | `implemented` | Extracts + runs query from LLM response |
| Retry loop with corrective feedback | `implemented` | Max 3 tries, feedback injection on no-results |
| Chainlit web UI | `implemented` | `on_message`, `set_starters`; streaming responses |
| Linter / formatter (ruff) | `planned` | Not yet configured in `pyproject.toml` |
| Type checker (mypy) | `planned` | Not yet configured |
| Tests (pytest) | `planned` | No test suite exists yet |
| CI/CD — Python (GitHub Actions) | `planned` | Only slide deploy workflow exists |
| Code profiling (flamegraph) | `planned` | Required by Week 16 task |
| Demo scripts reorganised to `demos/` | `planned` | Currently mixed with app code in `project/` |
| Project `README.md` for chatbot | `planned` | Existing README covers slides only |
| `chainlit.md` customised | `planned` | Still shows default Chainlit boilerplate |
| Branch protection on `main` | `planned` | Must be set on GitHub settings |

### 2.1 Status Tag Meanings

| Tag | Meaning |
|-----|---------|
| `implemented` | Fully working; do not rebuild |
| `baseline` | First working version; may be refined only if explicitly instructed |
| `planned` | Not started; do not build unless the current task explicitly requests it |
| `todo` | Accepted for near-term work; not yet started |
| `in_progress` | Actively being built — inspect branch before touching |
| `blocked` | Waiting on an external decision or dependency |
| `deprecated` | Do not use for new work |

---

## 3. Application Data Flow

```
User message (natural language)
    │
    ▼
[1] Embed question → 384-dim vector (FastEmbed, BAAI/bge-small-en-v1.5)
    │
    ▼
[2] Qdrant vector search → top-N query examples + schema shapes
    │
    ▼
[3] Format retrieved docs → inject into SYSTEM_PROMPT as context
    │
    ▼
[4] LLM (Mistral / Groq) → generate SPARQL query in markdown codeblock
    │                       (must include "#+ endpoint: <url>" comment)
    │
    ▼
[5] extract_sparql_queries() → parse endpoint URL + query body
    │
    ▼
[6] query_sparql() → execute against live endpoint
    │
    ├─ No results → append corrective message → retry (max 3 times) → go to [4]
    │
    └─ Results → append JSON results → LLM summarises → stream to user
```

---

## 4. Key Contracts

### 4.1 `load_chat_model(model: str) -> BaseChatModel`
- Input format: `"provider/model-name"` (e.g. `"mistralai/mistral-small-latest"`)
- Supported providers: `mistralai`, `groq`
- Raises `ValueError` for unknown providers
- **Do not add new providers without updating tests and `pyproject.toml` dependencies**

### 4.2 `index_endpoints() -> None`
- Deletes and recreates the Qdrant collection on every call
- Loads three doc types: `SparqlExamplesLoader`, `SparqlVoidShapesLoader`, `SparqlInfoLoader`
- Side effect: modifies `data/vectordb/` on disk
- **Only call explicitly; never call at module import time**

### 4.3 `retrieve_docs(question: str) -> list[ScoredPoint]`
- Returns `retrieved_docs_count` (3) results per `doc_type`
- Currently filters for two doc types: `"SPARQL endpoints query examples"` and
  `"SPARQL endpoints classes schema"`
- **Changing filter values will silently break retrieval quality**

### 4.4 `format_doc(doc: ScoredPoint) -> str`
- Pure function — no side effects
- Most testable function in the codebase; start tests here
- Returns a markdown snippet; format is tightly coupled to `SYSTEM_PROMPT` expectations

### 4.5 `execute_query(last_msg: str) -> list[dict[str, str]] | None`
- Parses SPARQL from LLM response markdown
- Returns `None` implicitly if no query is found — callers must handle `None`
- **Note:** current return type annotation `list[dict[str, str]]` is inaccurate — `None` is
  a valid return; fix this when adding type annotations

### 4.6 SPARQL query format expected by the system
```sparql
#+ endpoint: https://sparql.uniprot.org/sparql/
SELECT ?protein WHERE { ... }
```
The `#+ endpoint:` comment must be present inside the codeblock. The `SYSTEM_PROMPT` enforces
this via instruction; do not remove or rephrase that instruction.

---

## 5. Scope Guardrails

### 5.1 Absolute Rules

- Do not re-implement already implemented functions.
- Do not change the `SYSTEM_PROMPT` wording without explicit instruction — it controls LLM
  output format and breaking it will break SPARQL extraction.
- Do not make broad refactors during a scoped task.
- Do not update unrelated docs just because they could be improved.
- Do not add new biological endpoints without also updating `index_endpoints()` and tests.
- Do not move files without updating all imports and the CI workflow paths.
- Never hardcode API keys — always use environment variables loaded from `.env`.
- The `.env` file must never be committed; `.env.example` is the committed reference.

### 5.2 Branch-Awareness Rule

Before making changes, every contributor or agent must:

1. Check current branch (`git branch --show-current`).
2. Check what differs from `main` (`git diff main --name-only`).
3. Check `docs/FEATURE_STATUS.md` for what is already implemented.
4. Read the target file before proposing changes.

If branch code and documentation disagree:
- **Trust the code first.**
- Update documentation only after confirming with the task scope.

### 5.3 Files That Must Not Be Changed Without Explicit Instruction

| File | Reason |
|------|--------|
| `project/app.py` — `SYSTEM_PROMPT` constant | Changing it breaks SPARQL extraction |
| `project/data/vectordb/` | Runtime data; recreated by `index_endpoints()` |
| `project/uv.lock` | Auto-generated by `uv`; do not hand-edit |
| `.github/workflows/deploy.yml` | Slides deployment; unrelated to chatbot |

---

## 6. Coding Rules

### 6.1 Python Style
- Python 3.12 only (enforced by `requires-python = "==3.12.*"`)
- Line length: 88 characters (ruff default)
- Import order: stdlib → third-party → first-party
- Use `ruff` for linting and formatting (once configured)
- Type hints on all public functions
- Docstrings on all public functions and classes
- Keep functions small and independently testable
- No hidden side effects at module import time
- No hardcoded secrets or absolute file paths

### 6.2 Error Handling
- Do not use bare `except Exception` unless re-raising
- Log failures with `logging` (already configured in `app.py` with `%(asctime)s [%(levelname)s]`)
- `execute_query` silently returns `None` on no match — callers must handle it; do not change this silently

### 6.3 Environment Variables
- `MISTRAL_API_KEY` — required for Mistral AI provider
- `GROQ_API_KEY` — required for Groq provider
- Copy `.env.example` to `.env` and fill in values; never commit `.env`

### 6.4 Tests
- Framework: `pytest` (once installed)
- Test files: `tests/unit/test_<module_name>.py`
- Tests must be isolated; no real LLM calls; no real network calls unless integration-scoped
- Mock external calls: Qdrant queries, LLM inference, SPARQL endpoint HTTP requests
- Start with pure functions: `format_doc`, `load_chat_model` (error path)

### 6.5 Commits and Branches
- See `CONTRIBUTING.md` for full workflow
- All changes to production code via a PR referencing an Issue
- Commit message format: `type(scope): short description`
  - Types: `feat`, `fix`, `refactor`, `test`, `ci`, `docs`, `chore`
  - Examples: `feat(app): add query result caching`, `fix(app): handle None from execute_query`

---

## 7. Required Pre-Task Reading Order

Before any change, read in this order:

1. `AGENTS.md` ← this file
2. `README.md`
3. `docs/FEATURE_STATUS.md`
4. `CHANGELOG.md`
5. `project/app.py` — the target file for most tasks
6. Current task instructions

---

## 8. Instructions for AI Coding Agents

### 8.1 Mandatory Workflow

1. Read the **AI Agent Quick Brief** at the top of this file first.
2. Run `git branch --show-current` and `git diff main --name-only`.
3. Read `docs/FEATURE_STATUS.md` to confirm what is already implemented.
4. Read the target file in full before proposing any edit.
4. State exactly which files you will modify before modifying them.
5. Implement only scoped changes — do not improve unrelated areas opportunistically.
6. Write or update tests in parallel with implementation.
7. Run `ruff check` and `mypy` before marking a task done (once tooling is set up).

### 8.2 Mandatory Reporting Format

Every coding agent session must end with:

- **Scope completed** — what was done
- **Files changed** — exhaustive list
- **Tests added/updated** — what coverage was added
- **Verification performed** — lint/mypy/test output
- **Follow-up items** — anything deferred or flagged
- **Confirmation** that no files outside scope were changed

### 8.3 Prohibited AI Behaviours

- Rebuilding implemented functions because docs or README appear outdated
- Implementing `planned` features that the current task did not request
- Rewriting `SYSTEM_PROMPT` without instruction
- Changing `uv.lock` or `data/vectordb/` by hand
- Using absolute paths in code
- Adding API keys or credentials to any tracked file
- Touching the `deploy.yml` workflow unless the task is specifically about slides CI

### 8.4 Context Loss Recovery

If context is lost mid-session:

1. Read this file again.
2. Read `docs/FEATURE_STATUS.md`.
3. Run `git status` and `git diff`.
4. Read `project/app.py` top-to-bottom.
5. Continue only after confirming the current implementation state.

**Never assume a missing explanation means missing implementation.**

---

## 9. Definition of Done

A task is only done if:

- [ ] Scope is fully implemented
- [ ] Tests are added or updated
- [ ] No files outside the stated scope were changed
- [ ] `ruff check` passes with zero errors (once configured)
- [ ] `mypy` passes with zero errors (once configured)
- [ ] `docs/FEATURE_STATUS.md` is updated with new status labels
- [ ] `CHANGELOG.md` has a new entry describing the change
- [ ] The summary states what was and was not changed

---

## 10. Quick Reference for New Contributors

Read only these five files to get up to speed:

1. `AGENTS.md` ← this file
2. `README.md`
3. `docs/FEATURE_STATUS.md`
4. `CHANGELOG.md`
5. `project/app.py`

This is enough to start a scoped task without reading the full codebase.

---

## 11. Maintainer Note

If an agent starts rebuilding functions that already exist, or implements `planned` features
without instruction, stop it immediately and redirect it to:

1. Section 2 of this file (Current Project Status)
2. `docs/FEATURE_STATUS.md`
3. Section 5 of this file (Scope Guardrails)

This document exists specifically to prevent duplicated implementation, context loss, and
unauthorised changes.
